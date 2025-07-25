


import { useMutation, useQueryClient } from "@tanstack/react-query";
import posthog from "posthog-js";
import { DEFAULT_SETTINGS } from "#/services/settings";
import OpenHands from "#/api/open-hands";
import { PostSettings, PostApiSettings } from "#/types/settings";
import { useSettings } from "../query/use-settings";

const saveSettingsMutationFn = async (settings: Partial<PostSettings>) => {
  const apiSettings: Partial<PostApiSettings> = {
    llm_model: settings.LLM_MODEL,
    llm_base_url: settings.LLM_BASE_URL,
    agent: settings.AGENT || DEFAULT_SETTINGS.AGENT,
    language: settings.LANGUAGE || DEFAULT_SETTINGS.LANGUAGE,
    confirmation_mode: settings.CONFIRMATION_MODE,
    security_analyzer: settings.SECURITY_ANALYZER,
    llm_api_key:
      settings.llm_api_key === ""
        ? ""
        : settings.llm_api_key?.trim() || undefined,
    remote_runtime_resource_factor: settings.REMOTE_RUNTIME_RESOURCE_FACTOR,
    enable_default_condenser: settings.ENABLE_DEFAULT_CONDENSER,
    enable_sound_notifications: settings.ENABLE_SOUND_NOTIFICATIONS,
    user_consents_to_analytics: settings.user_consents_to_analytics,
    provider_tokens_set: settings.PROVIDER_TOKENS_SET,
    mcp_config: settings.MCP_CONFIG,
    enable_proactive_conversation_starters:
      settings.ENABLE_PROACTIVE_CONVERSATION_STARTERS,
    search_api_key: settings.SEARCH_API_KEY?.trim() || "",
    max_budget_per_task: settings.MAX_BUDGET_PER_TASK,
    max_token: settings.MAX_TOKEN,
    max_input_tokens: settings.MAX_INPUT_TOKENS,
    max_output_tokens: settings.MAX_OUTPUT_TOKENS,
    num_retries: settings.NUM_RETRIES,
    retry_min_wait: settings.RETRY_MIN_WAIT,
    retry_max_wait: settings.RETRY_MAX_WAIT,
    retry_multiplier: settings.RETRY_MULTIPLIER,
  };

  await OpenHands.saveSettings(apiSettings);
};

export const useSaveSettings = () => {
  const queryClient = useQueryClient();
  const { data: currentSettings } = useSettings();

  return useMutation({
    mutationFn: async (settings: Partial<PostSettings>) => {
      const newSettings = { ...currentSettings, ...settings };

      // Track MCP configuration changes
      if (
        settings.MCP_CONFIG &&
        currentSettings?.MCP_CONFIG !== settings.MCP_CONFIG
      ) {
        const hasMcpConfig = !!settings.MCP_CONFIG;
        const sseServersCount = settings.MCP_CONFIG?.sse_servers?.length || 0;
        const stdioServersCount =
          settings.MCP_CONFIG?.stdio_servers?.length || 0;

        posthog.capture("mcp_config_changed", {
          has_mcp_config: hasMcpConfig,
          sse_servers_count: sseServersCount,
          stdio_servers_count: stdioServersCount,
        });
      }

      await saveSettingsMutationFn(newSettings);

      // Invalidate the settings query
      queryClient.invalidateQueries(["settings"]);

      // Track settings changes
      posthog.capture("settings_changed", {
        llm_model: newSettings.LLM_MODEL,
        language: newSettings.LANGUAGE,
        confirmation_mode: newSettings.CONFIRMATION_MODE,
        enable_sound_notifications: newSettings.ENABLE_SOUND_NOTIFICATIONS,
        enable_proactive_conversation_starters:
          newSettings.ENABLE_PROACTIVE_CONVERSATION_STARTERS,
        user_consents_to_analytics: newSettings.USER_CONSENTS_TO_ANALYTICS,
      });

      return newSettings;
    },
  });
};
