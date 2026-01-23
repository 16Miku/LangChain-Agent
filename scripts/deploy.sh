#!/bin/bash
# ============================================================
# My-Chat-LangChain V10 部署脚本
# Render + Supabase 一键部署
# ============================================================
# 使用方法:
#   ./scripts/deploy.sh              # 完整部署
#   ./scripts/deploy.sh --dry-run    # 模拟运行，不执行实际操作
#   ./scripts/deploy.sh --services   # 仅部署服务
#   ./scripts/deploy.sh --database   # 仅初始化数据库
#   ./scripts/deploy.sh --verify     # 仅验证部署状态
# ============================================================

set -e  # 遇到错误立即退出

# ============================================================
# 颜色定义
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================
# 工具函数
# ============================================================

# 打印带颜色的信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

step() {
    echo -e "\n${PURPLE}==>${NC} ${CYAN}$1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "命令 '$1' 未找到，请先安装"
        return 1
    fi
    return 0
}

# 检查环境变量
check_env_var() {
    local var_name=$1
    local var_value="${!var_name}"
    if [ -z "$var_value" ]; then
        error "环境变量 $var_name 未设置"
        return 1
    fi
    success "环境变量 $var_name 已设置"
    return 0
}

# 进度条
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))

    printf "\r["
    printf "%${filled}s" | tr ' ' '='
    printf "%${empty}s" | tr ' ' '-'
    printf "] %d%%" $percentage
}

# ============================================================
# 全局变量
# ============================================================
DRY_RUN=false
DEPLOY_SERVICES=true
DEPLOY_DATABASE=true
VERIFY_ONLY=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 服务列表
SERVICES=(
    "auth-service:8001"
    "chat-service:8002"
    "rag-service:8004"
    "presentation-service:8005"
)

# ============================================================
# 参数解析
# ============================================================
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                warning "模拟运行模式 - 不会执行实际操作"
                shift
                ;;
            --services)
                DEPLOY_DATABASE=false
                shift
                ;;
            --database)
                DEPLOY_SERVICES=false
                shift
                ;;
            --verify)
                VERIFY_ONLY=true
                DEPLOY_SERVICES=false
                DEPLOY_DATABASE=false
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
My-Chat-LangChain V10 部署脚本

使用方法:
    ./scripts/deploy.sh [选项]

选项:
    --dry-run     模拟运行，不执行实际操作
    --services    仅部署 Render 服务
    --database    仅初始化 Supabase 数据库
    --verify      仅验证部署状态
    -h, --help    显示帮助信息

环境变量 (必需):
    RENDER_API_KEY        Render API 密钥
    SUPABASE_URL          Supabase 项目 URL
    SUPABASE_ANON_KEY     Supabase 匿名密钥
    SUPABASE_SERVICE_KEY  Supabase 服务密钥 (用于数据库操作)

环境变量 (可选):
    GOOGLE_API_KEY        Google Gemini API 密钥
    E2B_API_KEY           E2B 沙箱 API 密钥
    SERPER_API_KEY        Serper 搜索 API 密钥

示例:
    # 完整部署
    ./scripts/deploy.sh

    # 模拟运行
    ./scripts/deploy.sh --dry-run

    # 仅部署服务
    ./scripts/deploy.sh --services

    # 仅验证状态
    ./scripts/deploy.sh --verify
EOF
}

# ============================================================
# 环境检查
# ============================================================
check_prerequisites() {
    step "检查部署前置条件"

    local has_error=false

    # 检查必要的命令
    info "检查必要的命令..."
    for cmd in curl jq git; do
        if ! check_command "$cmd"; then
            has_error=true
        fi
    done

    # 检查必要的环境变量
    info "检查环境变量..."

    # Render 相关
    if [ "$DEPLOY_SERVICES" = true ]; then
        if ! check_env_var "RENDER_API_KEY"; then
            has_error=true
        fi
    fi

    # Supabase 相关
    if [ "$DEPLOY_DATABASE" = true ]; then
        for var in SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_KEY; do
            if ! check_env_var "$var"; then
                has_error=true
            fi
        done
    fi

    # 检查项目文件
    info "检查项目文件..."
    if [ ! -f "$PROJECT_ROOT/render.yaml" ]; then
        warning "render.yaml 未找到，将使用 API 创建服务"
    fi

    if [ ! -f "$PROJECT_ROOT/scripts/setup-supabase.sql" ]; then
        error "setup-supabase.sql 未找到"
        has_error=true
    fi

    if [ "$has_error" = true ]; then
        error "前置条件检查失败，请修复上述问题后重试"
        exit 1
    fi

    success "前置条件检查通过"
}

# ============================================================
# Supabase 数据库初始化
# ============================================================
init_supabase_database() {
    step "初始化 Supabase 数据库"

    if [ "$DRY_RUN" = true ]; then
        info "[DRY-RUN] 将执行 SQL 脚本: $PROJECT_ROOT/scripts/setup-supabase.sql"
        return 0
    fi

    local sql_file="$PROJECT_ROOT/scripts/setup-supabase.sql"

    # 提取 Supabase 项目 ID
    local project_ref=$(echo "$SUPABASE_URL" | sed -n 's/.*\/\/\([^.]*\).*/\1/p')

    if [ -z "$project_ref" ]; then
        error "无法从 SUPABASE_URL 提取项目 ID"
        return 1
    fi

    info "Supabase 项目 ID: $project_ref"
    info "执行数据库初始化脚本..."

    # 使用 Supabase REST API 执行 SQL
    # 注意: 实际生产中建议使用 supabase CLI 或直接连接数据库
    local response=$(curl -s -X POST \
        "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
        -H "apikey: ${SUPABASE_SERVICE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": $(cat "$sql_file" | jq -Rs .)}" \
        2>&1)

    # 检查响应
    if echo "$response" | grep -q "error"; then
        warning "SQL 执行可能有错误，请检查 Supabase 控制台"
        warning "响应: $response"

        # 提供手动执行指南
        info "您也可以手动执行 SQL:"
        info "1. 登录 Supabase 控制台: https://supabase.com/dashboard"
        info "2. 进入项目 -> SQL Editor"
        info "3. 复制并执行 $sql_file 中的内容"
    else
        success "数据库初始化完成"
    fi
}

# ============================================================
# Render 服务部署
# ============================================================
deploy_render_services() {
    step "部署 Render 服务"

    if [ "$DRY_RUN" = true ]; then
        info "[DRY-RUN] 将部署以下服务:"
        for service_info in "${SERVICES[@]}"; do
            local service_name="${service_info%%:*}"
            local service_port="${service_info##*:}"
            info "  - $service_name (端口: $service_port)"
        done
        return 0
    fi

    # 检查是否有 render.yaml
    if [ -f "$PROJECT_ROOT/render.yaml" ]; then
        info "使用 render.yaml 进行部署..."
        deploy_with_render_yaml
    else
        info "使用 Render API 进行部署..."
        deploy_with_render_api
    fi
}

deploy_with_render_yaml() {
    # 使用 Render Blueprint 部署
    info "触发 Render Blueprint 部署..."

    local response=$(curl -s -X POST \
        "https://api.render.com/v1/blueprints" \
        -H "Authorization: Bearer ${RENDER_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"my-chat-langchain-v10\",
            \"repo\": \"$(git config --get remote.origin.url)\",
            \"branch\": \"main\"
        }" 2>&1)

    if echo "$response" | grep -q "id"; then
        local blueprint_id=$(echo "$response" | jq -r '.id')
        success "Blueprint 创建成功: $blueprint_id"
        info "请在 Render 控制台查看部署进度"
    else
        warning "Blueprint 创建可能失败: $response"
        info "请手动在 Render 控制台导入 render.yaml"
    fi
}

deploy_with_render_api() {
    local total=${#SERVICES[@]}
    local current=0

    for service_info in "${SERVICES[@]}"; do
        local service_name="${service_info%%:*}"
        local service_port="${service_info##*:}"

        ((current++))
        info "部署服务 ($current/$total): $service_name"

        # 创建或更新服务
        local response=$(curl -s -X POST \
            "https://api.render.com/v1/services" \
            -H "Authorization: Bearer ${RENDER_API_KEY}" \
            -H "Content-Type: application/json" \
            -d "{
                \"type\": \"web_service\",
                \"name\": \"$service_name\",
                \"repo\": \"$(git config --get remote.origin.url)\",
                \"branch\": \"main\",
                \"rootDir\": \"backend/$service_name\",
                \"env\": \"python\",
                \"buildCommand\": \"pip install -r requirements.txt\",
                \"startCommand\": \"uvicorn app.main:app --host 0.0.0.0 --port $service_port\",
                \"envVars\": [
                    {\"key\": \"DATABASE_URL\", \"value\": \"${SUPABASE_URL}\"},
                    {\"key\": \"GOOGLE_API_KEY\", \"value\": \"${GOOGLE_API_KEY:-}\"},
                    {\"key\": \"JWT_SECRET\", \"value\": \"${JWT_SECRET:-$(openssl rand -hex 32)}\"}
                ]
            }" 2>&1)

        if echo "$response" | grep -q "id"; then
            local service_id=$(echo "$response" | jq -r '.id')
            success "服务 $service_name 创建成功: $service_id"
        else
            warning "服务 $service_name 创建可能失败: $response"
        fi

        show_progress $current $total
    done

    echo ""  # 换行
    success "所有服务部署请求已发送"
}

# ============================================================
# 部署验证
# ============================================================
verify_deployment() {
    step "验证部署状态"

    local all_healthy=true

    # 验证 Render 服务
    info "检查 Render 服务状态..."

    if [ "$DRY_RUN" = true ]; then
        info "[DRY-RUN] 将检查以下服务健康状态:"
        for service_info in "${SERVICES[@]}"; do
            local service_name="${service_info%%:*}"
            info "  - $service_name"
        done
        return 0
    fi

    # 获取服务列表
    local services_response=$(curl -s \
        "https://api.render.com/v1/services" \
        -H "Authorization: Bearer ${RENDER_API_KEY}" \
        2>&1)

    if echo "$services_response" | grep -q "error"; then
        warning "无法获取服务列表: $services_response"
        all_healthy=false
    else
        # 检查每个服务
        for service_info in "${SERVICES[@]}"; do
            local service_name="${service_info%%:*}"
            local service_status=$(echo "$services_response" | jq -r ".[] | select(.name==\"$service_name\") | .status")

            if [ "$service_status" = "live" ]; then
                success "服务 $service_name: 运行中"
            elif [ -n "$service_status" ]; then
                warning "服务 $service_name: $service_status"
                all_healthy=false
            else
                warning "服务 $service_name: 未找到"
                all_healthy=false
            fi
        done
    fi

    # 验证 Supabase 连接
    info "检查 Supabase 连接..."

    local supabase_response=$(curl -s \
        "${SUPABASE_URL}/rest/v1/" \
        -H "apikey: ${SUPABASE_ANON_KEY}" \
        2>&1)

    if echo "$supabase_response" | grep -q "error"; then
        warning "Supabase 连接失败: $supabase_response"
        all_healthy=false
    else
        success "Supabase 连接正常"
    fi

    # 健康检查端点
    info "执行健康检查..."

    for service_info in "${SERVICES[@]}"; do
        local service_name="${service_info%%:*}"

        # 获取服务 URL
        local service_url=$(echo "$services_response" | jq -r ".[] | select(.name==\"$service_name\") | .serviceDetails.url")

        if [ -n "$service_url" ] && [ "$service_url" != "null" ]; then
            local health_response=$(curl -s -o /dev/null -w "%{http_code}" "${service_url}/health" 2>&1)

            if [ "$health_response" = "200" ]; then
                success "健康检查 $service_name: OK"
            else
                warning "健康检查 $service_name: HTTP $health_response"
                all_healthy=false
            fi
        fi
    done

    # 总结
    echo ""
    if [ "$all_healthy" = true ]; then
        success "所有服务运行正常!"
    else
        warning "部分服务可能存在问题，请检查 Render 控制台"
    fi
}

# ============================================================
# 回滚功能
# ============================================================
rollback() {
    step "执行回滚"

    warning "回滚功能需要手动在 Render 控制台执行"
    info "步骤:"
    info "1. 登录 Render 控制台: https://dashboard.render.com"
    info "2. 选择需要回滚的服务"
    info "3. 进入 Deploys 标签页"
    info "4. 选择之前的成功部署，点击 'Rollback'"
}

# ============================================================
# 主函数
# ============================================================
main() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     My-Chat-LangChain V10 部署脚本                         ║${NC}"
    echo -e "${CYAN}║     Render + Supabase 一键部署                             ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # 解析参数
    parse_args "$@"

    # 仅验证模式
    if [ "$VERIFY_ONLY" = true ]; then
        verify_deployment
        exit 0
    fi

    # 检查前置条件
    check_prerequisites

    # 部署数据库
    if [ "$DEPLOY_DATABASE" = true ]; then
        init_supabase_database
    fi

    # 部署服务
    if [ "$DEPLOY_SERVICES" = true ]; then
        deploy_render_services
    fi

    # 验证部署
    verify_deployment

    # 完成
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     部署完成!                                              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    info "后续步骤:"
    info "1. 在 Render 控制台查看部署日志"
    info "2. 配置自定义域名 (可选)"
    info "3. 设置监控告警 (可选)"
    info ""
    info "有用的链接:"
    info "  - Render 控制台: https://dashboard.render.com"
    info "  - Supabase 控制台: https://supabase.com/dashboard"
}

# 执行主函数
main "$@"
