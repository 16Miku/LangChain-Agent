'use client';

// ============================================================
// Settings Page
// ============================================================

import { useState } from 'react';
import { Moon, Sun, Monitor, Save, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useSettingsStore, useAuthStore } from '@/lib/stores';
import { cn } from '@/lib/utils';

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { defaultModel, setDefaultModel, voiceEnabled, setVoiceEnabled } = useSettingsStore();
  const { user } = useAuthStore();

  const [isSaving, setIsSaving] = useState(false);
  const [apiKeys, setApiKeys] = useState({
    GOOGLE_API_KEY: '',
    E2B_API_KEY: '',
    BRIGHT_DATA_API_KEY: '',
  });

  const handleSaveApiKeys = async () => {
    setIsSaving(true);
    // TODO: Implement API key saving to backend
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
  };

  const themeOptions = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'System', icon: Monitor },
  ] as const;

  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Manage your account and preferences</p>
        </div>

        <Separator />

        {/* Profile Section */}
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>Your account information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div>
                <p className="font-medium">{user?.username || 'User'}</p>
                <p className="text-sm text-muted-foreground">{user?.email || 'user@example.com'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Appearance Section */}
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>Customize how Stream-Agent looks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <label className="text-sm font-medium">Theme</label>
              <div className="flex gap-2">
                {themeOptions.map((option) => (
                  <Button
                    key={option.value}
                    variant={theme === option.value ? 'default' : 'outline'}
                    className={cn(
                      'flex-1',
                      theme === option.value && 'ring-2 ring-primary ring-offset-2'
                    )}
                    onClick={() => setTheme(option.value)}
                  >
                    <option.icon className="mr-2 h-4 w-4" />
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Model Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Model Settings</CardTitle>
            <CardDescription>Configure the AI model</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Default Model</label>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2"
              >
                <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite</option>
                <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Voice Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Voice Settings</CardTitle>
            <CardDescription>Configure voice input and output</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Enable Voice</p>
                <p className="text-sm text-muted-foreground">
                  Allow voice input and text-to-speech output
                </p>
              </div>
              <Button
                variant={voiceEnabled ? 'default' : 'outline'}
                onClick={() => setVoiceEnabled(!voiceEnabled)}
              >
                {voiceEnabled ? 'Enabled' : 'Disabled'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* API Keys Section */}
        <Card>
          <CardHeader>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>Manage your API keys for external services</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Google API Key</label>
              <Input
                type="password"
                placeholder="Enter your Google API key"
                value={apiKeys.GOOGLE_API_KEY}
                onChange={(e) => setApiKeys({ ...apiKeys, GOOGLE_API_KEY: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">E2B API Key</label>
              <Input
                type="password"
                placeholder="Enter your E2B API key"
                value={apiKeys.E2B_API_KEY}
                onChange={(e) => setApiKeys({ ...apiKeys, E2B_API_KEY: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">BrightData API Key</label>
              <Input
                type="password"
                placeholder="Enter your BrightData API key"
                value={apiKeys.BRIGHT_DATA_API_KEY}
                onChange={(e) => setApiKeys({ ...apiKeys, BRIGHT_DATA_API_KEY: e.target.value })}
              />
            </div>
            <Button onClick={handleSaveApiKeys} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save API Keys
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
