

import React from "react";
import { useTranslation } from "react-i18next";
import { useSettings } from "#/hooks/query/use-settings";
import { useSaveSettings } from "#/hooks/mutation/use-save-settings";
import { SettingsInput } from "../settings-input";
import { SettingsSwitch } from "../settings-switch";
import { I18nKey } from "#/i18n/declaration";

export function SystemSettings() {
  const { t } = useTranslation();
  const { data: settings } = useSettings();
  const saveSettings = useSaveSettings();

  if (!settings) {
    return null;
  }

  const handleInputChange = (field: string, value: string | number | boolean) => {
    saveSettings.mutate({ [field]: value });
  };

  return (
    <div className="px-11 py-9 flex flex-col gap-6">
      <h2 className="text-lg font-semibold">{t(I18nKey.SETTINGS$SYSTEM_TITLE)}</h2>

      <div className="flex flex-col gap-4">
        <SettingsInput
          label={t(I18nKey.SETTINGS$SYSTEM_MAX_TOKENS)}
          value={settings.MAX_TOKEN ?? ""}
          onChange={(e) => handleInputChange("MAX_TOKEN", e.target.value)}
          type="number"
          placeholder="Max tokens"
        />

        <SettingsInput
          label={t(I18nKey.SETTINGS$SYSTEM_MAX_INPUT_TOKENS)}
          value={settings.MAX_INPUT_TOKENS ?? ""}
          onChange={(e) => handleInputChange("MAX_INPUT_TOKENS", e.target.value)}
          type="number"
          placeholder="Max input tokens"
        />

        <SettingsInput
          label={t(I18nKey.SETTINGS$SYSTEM_MAX_OUTPUT_TOKENS)}
          value={settings.MAX_OUTPUT_TOKENS ?? ""}
          onChange={(e) => handleInputChange("MAX_OUTPUT_TOKENS", e.target.value)}
          type="number"
          placeholder="Max output tokens"
        />

        <h3 className="text-sm font-medium mt-6">{t(I18nKey.SETTINGS$SYSTEM_RETRY_CONFIG)}</h3>

        <SettingsInput
          label={t(I18nKey.SETTINGS$SYSTEM_NUM_RETRIES)}
          value={settings.NUM_RETRIES ?? ""}
          onChange={(e) => handleInputChange("NUM_RETRIES", e.target.value)}
          type="number"
          placeholder="Number of retries"
        />

        <SettingsInput
          label={t(I18nKey.SETTINGS$SYSTEM_RETRY_MIN_WAIT)}
          value={settings.RETRY_MIN_WAIT ?? ""}
          onChange={(e) => handleInputChange("RETRY_MIN_WAIT", e.target.value)}
          type="number"
          placeholder="Minimum wait time (ms)"
        />

        <SettingsInput
          label={t(I18nKey.SETTINGS$SYSTEM_RETRY_MAX_WAIT)}
          value={settings.RETRY_MAX_WAIT ?? ""}
          onChange={(e) => handleInputChange("RETRY_MAX_WAIT", e.target.value)}
          type="number"
          placeholder="Maximum wait time (ms)"
        />

        <SettingsInput
          label={t(I18nKey.SETTINGS$SYSTEM_RETRY_MULTIPLIER)}
          value={settings.RETRY_MULTIPLIER ?? ""}
          onChange={(e) => handleInputChange("RETRY_MULTIPLIER", e.target.value)}
          type="number"
          placeholder="Retry multiplier"
        />
      </div>
    </div>
  );
}
