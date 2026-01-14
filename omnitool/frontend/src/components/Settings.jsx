import { useState } from 'react'
import '../styles/Settings.css'

const MODEL_OPTIONS = [
  // Cloud API models
  { value: "omniparser + gpt-4o", label: "OpenAI GPT-4o" },
  { value: "omniparser + o1", label: "OpenAI o1" },
  { value: "omniparser + o3-mini", label: "OpenAI o3-mini" },
  { value: "claude-3-5-sonnet-20241022", label: "Claude 3.5 Sonnet" },

  // Text-only local models (RECOMMENDED)
  { value: "omniparser + ollama/llama3.1:8b-instruct-q4_K_M", label: "Ollama Llama 3.1 8B (text)" },
  { value: "omniparser + ollama/deepseek-r1:7b", label: "Ollama DeepSeek R1 7B" },
  { value: "omniparser + ollama/qwen2.5:7b-instruct", label: "Ollama Qwen 2.5 7B" },

  // Vision models (optional)
  { value: "omniparser + ollama/llama3.2-vision:latest", label: "Ollama Llama 3.2 Vision 11B" },
  { value: "omniparser + hf/meta-llama/Llama-3.1-8B-Instruct", label: "HF Llama 3.1 8B" },
]

const PROVIDER_MAP = {
  "claude-3-5-sonnet-20241022": "anthropic",
  "omniparser + gpt-4o": "openai",
  "omniparser + o1": "openai",
  "omniparser + o3-mini": "openai",
  "omniparser + ollama/": "ollama",
  "omniparser + hf/": "huggingface",
}

function Settings({ settings, onUpdate, agentStatus }) {
  const [localSettings, setLocalSettings] = useState(settings)
  const [isExpanded, setIsExpanded] = useState(true)

  const handleChange = (field, value) => {
    const updated = { ...localSettings, [field]: value }

    // Auto-select provider based on model
    if (field === 'model') {
      for (const [key, provider] of Object.entries(PROVIDER_MAP)) {
        if (value.includes(key)) {
          updated.provider = provider
          break
        }
      }
    }

    setLocalSettings(updated)
  }

  const handleSave = () => {
    onUpdate(localSettings)
  }

  return (
    <div className="settings-container">
      <div className="settings-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h2>⚙️ Settings</h2>
        <span className="toggle-icon">{isExpanded ? '▼' : '▶'}</span>
      </div>

      {isExpanded && (
        <div className="settings-content">
          <div className="setting-group">
            <label>Model</label>
            <select
              value={localSettings.model}
              onChange={(e) => handleChange('model', e.target.value)}
              disabled={agentStatus === 'running'}
            >
              {MODEL_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="setting-group">
            <label>API Provider</label>
            <select
              value={localSettings.provider}
              onChange={(e) => handleChange('provider', e.target.value)}
              disabled={agentStatus === 'running'}
            >
              <option value="anthropic">Anthropic</option>
              <option value="openai">OpenAI</option>
              <option value="ollama">Ollama (Local)</option>
              <option value="huggingface">Hugging Face</option>
            </select>
          </div>

          <div className="setting-group">
            <label>API Key</label>
            <input
              type="password"
              value={localSettings.api_key || ''}
              onChange={(e) => handleChange('api_key', e.target.value)}
              placeholder="Enter API key (leave empty for local models)"
              disabled={agentStatus === 'running'}
            />
          </div>

          <div className="setting-group">
            <label>Max Tokens</label>
            <input
              type="number"
              value={localSettings.max_tokens}
              onChange={(e) => handleChange('max_tokens', parseInt(e.target.value))}
              min="256"
              max="8192"
              disabled={agentStatus === 'running'}
            />
          </div>

          <div className="setting-group">
            <label>Recent Screenshots</label>
            <input
              type="number"
              value={localSettings.only_n_images}
              onChange={(e) => handleChange('only_n_images', parseInt(e.target.value))}
              min="0"
              max="10"
              disabled={agentStatus === 'running'}
            />
            <small>Number of recent screenshots to include in context</small>
          </div>

          <button
            onClick={handleSave}
            className="btn btn-primary save-button"
            disabled={agentStatus === 'running'}
          >
            Save Settings
          </button>

          <div className="agent-status-display">
            <strong>Status:</strong>{' '}
            <span className={`status-badge status-${agentStatus}`}>
              {agentStatus}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default Settings
