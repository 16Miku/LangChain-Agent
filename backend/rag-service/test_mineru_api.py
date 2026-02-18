"""
测试 MinerU API 连接
"""
import httpx
import asyncio

API_KEY = ""

async def test_api():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0, proxy=None) as client:
        # 测试批量上传获取 batch_id
        print("=" * 60)
        print("测试批量上传 (获取 batch_id)")
        print("=" * 60)

        url = "https://mineru.net/api/v4/file-urls/batch"
        payload = {"files": [{"name": "test.pdf"}]}

        response = await client.post(url, headers=headers, json=payload)
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {data}")

        if data.get("code") == 0:
            batch_id = data.get("data", {}).get("batch_id")
            print(f"\nBatch ID: {batch_id}")

            # 测试不同的批量查询端点
            print("\n" + "=" * 60)
            print("测试批量查询端点")
            print("=" * 60)

            query_endpoints = [
                f"https://mineru.net/api/v4/extract-results/batch/{batch_id}",  # 正确的端点
                f"https://mineru.net/api/v4/extract/batch/task/{batch_id}",
            ]

            for query_url in query_endpoints:
                print(f"\n测试: {query_url}")
                try:
                    resp = await client.get(query_url, headers=headers)
                    print(f"  状态码: {resp.status_code}")
                    print(f"  响应: {resp.text[:500]}")
                except Exception as e:
                    print(f"  错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
