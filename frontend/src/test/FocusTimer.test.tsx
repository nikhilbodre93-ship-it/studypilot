import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "@/components/ui/Toast";
import { FocusTimerPage } from "@/pages/FocusTimerPage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>{ui}</ToastProvider>
    </QueryClientProvider>
  );
};

describe("FocusTimer Component", () => {
  it("renders with default 25:00 digits and duration preset buttons", () => {
    renderWithProviders(<FocusTimerPage initialMinutes={25} />);

    expect(screen.getByText("Focus timer")).toBeInTheDocument();
    expect(screen.getByText("25:00")).toBeInTheDocument();
    expect(screen.getByText("25 min")).toBeInTheDocument();
    expect(screen.getByText("45 min")).toBeInTheDocument();
    expect(screen.getByText("60 min")).toBeInTheDocument();
    expect(screen.getByText("Start")).toBeInTheDocument();
  });

  it("changes target digits when preset button is clicked", () => {
    renderWithProviders(<FocusTimerPage initialMinutes={25} />);

    const btn45 = screen.getByText("45 min");
    fireEvent.click(btn45);
    expect(screen.getByText("45:00")).toBeInTheDocument();

    const btn60 = screen.getByText("60 min");
    fireEvent.click(btn60);
    expect(screen.getByText("60:00")).toBeInTheDocument();
  });

  it("toggles Start to Pause on click", () => {
    renderWithProviders(<FocusTimerPage initialMinutes={25} />);

    const startBtn = screen.getByText("Start");
    fireEvent.click(startBtn);
    expect(screen.getByText("Pause")).toBeInTheDocument();
  });
});
