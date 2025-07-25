

import { useQuery } from "@tanstack/react-query";
import React from "react";
import posthog from "posthog-js";
import OpenHands from "#/api/open-hands";
import { DEFAULT_SETTINGS } from "#/services/settings";
import { useIsOnTosPage } from "#/hooks/use-is-on-tos-page";
import { Settings } from "#/types/settings";
import { useIsAuthed } from "./use-is-authed";

const getSettingsQueryFn = async (): Promise<Settings> => {
  const apiSettings = await OpenHands.getSettings();

  return {
    LLM_MODEL: apiSettings.llm_model,
    LLM_BASE_URL: apiSettings.llm_base_url,
    AGENT: apiSettings.agent,
    LANGUAGE: apiSettings.language,
    CONFIRMATION_MODE: apiSettings.confirmation_mode,
    SECURITY_ANALYZER: apiSettings.security_analyzer,
    LLM_API_KEY_SET: apiSettings.llm_api_key_set,
    SEARCH_API_KEY_SET: apiSettings.search_api_key_set,
    REMOTE_RUNTIME_RESOURCE_FACTOR: apiSettings.remote_runtime_resource_factor,
    PROVIDER_TOKENS_SET: apiSettings.provider_tokens_set,
    ENABLE_DEFAULT_CONDENSER: apiSettings.enable_default_condenser,
    ENABLE_SOUND_NOTIFICATIONS: apiSettings.enable_sound_notifications,
    ENABLE_PROACTIVE_CONVERSATION_STARTERS:
      apiSettings.enable_proactive_conversation_starters,
    USER_CONSENTS_TO_ANALYTICS: apiSettings.user_consents_to_analytics,
    SEARCH_API_KEY: apiSettings.search_api_key || "",
    MAX_BUDGET_PER_TASK: apiSettings.max_budget_per_task,
    EMAIL: apiSettings.email || "",
    EMAIL_VERIFIED: apiSettings.email_verified,
    MCP_CONFIG: apiSettings.mcp_config,
    IS_NEW_USER: false,
    MAX_TOKEN: apiSettings.max_token,
    MAX_INPUT_TOKENS: apiSettings.max_input_tokens,
    MAX_OUTPUT_TOKENS: apiSettings.max_output_tokens,
    NUM_RETRIES: apiSettings.num_retries,
    RETRY_MIN_WAIT: apiSettings.retry_min_wait,
    RETRY_MAX_WAIT: apiSettings.retry_max_wait,
    RETRY_MULTIPLIER: apiSettings.retry_multiplier,
  };
};

export const useSettings = () => {
  const isOnTosPage = useIsOnTosPage();
  const { data: userIsAuthenticated } = useIsAuthed();

  const query = useQuery({
    queryKey: ["settings"],
    queryFn: getSettingsQueryFn,
    // Only retry if the error is not a 404 because we
    // would want to show the modal immediately if the
    // settings are not found
    retry: (_, error) => error.status !== 404,
    refetchOnWindowFocus: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: !isOnTosPage && userIsAuthenticated,
  });

  React.useEffect(() => {
    if (query.data) {
      posthog.capture("settings_loaded");
    }
  }, [query.data]);

  return query;
};
