

import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SystemSettings } from "#/components/features/settings/system-settings/system-settings";
import { useSettings } from "#/hooks/query/use-settings";
import { useSaveSettings } from "#/hooks/mutation/use-save-settings";
import { I18nKey } from "#/i18n/declaration";
import { useTranslation } from "react-i18next";

vi.mock("#/hooks/query/use-settings");
vi.mock("#/hooks/mutation/use-save-settings");
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: I18nKey) => key,
  }),
}));

describe("SystemSettings", () => {
  const queryClient = new QueryClient();

  beforeEach(() => {
    (useSettings as any).mockReturnValue({
      data: {
        MAX_TOKEN: "2048",
        MAX_INPUT_TOKENS: "1024",
        MAX_OUTPUT_TOKENS: "1024",
        NUM_RETRIES: "3",
        RETRY_MIN_WAIT: "1000",
        RETRY_MAX_WAIT: "5000",
        RETRY_MULTIPLIER: "2",
      },
    });
    (useSaveSettings as any).mockReturnValue({
      mutate: vi.fn(),
    });
  });

  it("renders system settings form", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/settings/system"]}>
          <Routes>
            <Route path="/settings/system" element={<SystemSettings />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("SETTINGS$SYSTEM_TITLE")).toBeInTheDocument();
    });

    expect(screen.getByLabelText("Maximum Tokens")).toBeInTheDocument();
    expect(screen.getByLabelText("Maximum Input Tokens")).toBeInTheDocument();
    expect(screen.getByLabelText("Maximum Output Tokens")).toBeInTheDocument();
    expect(screen.getByLabelText("Number of Retries")).toBeInTheDocument();
    expect(screen.getByLabelText("Minimum Wait Time (ms)")).toBeInTheDocument();
    expect(screen.getByLabelText("Maximum Wait Time (ms)")).toBeInTheDocument();
    expect(screen.getByLabelText("Retry Multiplier")).toBeInTheDocument();
  });

  it("displays correct initial values", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/settings/system"]}>
          <Routes>
            <Route path="/settings/system" element={<SystemSettings />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByDisplayValue("2048")).toBeInTheDocument();
      expect(screen.getByDisplayValue("1024")).toBeInTheDocument();
      expect(screen.getByDisplayValue("1024")).toBeInTheDocument();
      expect(screen.getByDisplayValue("3")).toBeInTheDocument();
      expect(screen.getByDisplayValue("1000")).toBeInTheDocument();
      expect(screen.getByDisplayValue("5000")).toBeInTheDocument();
      expect(screen.getByDisplayValue("2")).toBeInTheDocument();
    });
  });

  it("calls saveSettings when input changes", async () => {
    const mockMutate = vi.fn();
    (useSaveSettings as any).mockReturnValue({ mutate: mockMutate });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/settings/system"]}>
          <Routes>
            <Route path="/settings/system" element={<SystemSettings />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByLabelText("Maximum Tokens")).toBeInTheDocument();
    });

    const input = screen.getByLabelText("Maximum Tokens") as HTMLInputElement;
    input.value = "4096";
    input.dispatchEvent(new Event("change"));

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith({ MAX_TOKEN: "4096" });
    });
  });
});
