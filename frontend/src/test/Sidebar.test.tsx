import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Sidebar } from "@/components/layout/Sidebar";
import { AuthProvider } from "@/context/AuthContext";

describe("Sidebar Navigation", () => {
  it("renders all 10 numbered navigation items matching the product spec", () => {
    const handleSelect = vi.fn();
    render(
      <AuthProvider>
        <Sidebar currentTab="dashboard" onSelectTab={handleSelect} />
      </AuthProvider>
    );

    // Verify brand logo
    expect(screen.getByText("studypilot")).toBeInTheDocument();

    // Verify all 10 items
    expect(screen.getByText("01")).toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("02")).toBeInTheDocument();
    expect(screen.getByText("My learning")).toBeInTheDocument();
    expect(screen.getByText("03")).toBeInTheDocument();
    expect(screen.getByText("Revision planner")).toBeInTheDocument();
    expect(screen.getByText("04")).toBeInTheDocument();
    expect(screen.getByText("Learning roadmap")).toBeInTheDocument();
    expect(screen.getByText("05")).toBeInTheDocument();
    expect(screen.getByText("Study notes")).toBeInTheDocument();
    expect(screen.getByText("06")).toBeInTheDocument();
    expect(screen.getByText("Practice quizzes")).toBeInTheDocument();
    expect(screen.getByText("07")).toBeInTheDocument();
    expect(screen.getByText("Flashcards")).toBeInTheDocument();
    expect(screen.getByText("08")).toBeInTheDocument();
    expect(screen.getByText("AI tutor")).toBeInTheDocument();
    expect(screen.getByText("09")).toBeInTheDocument();
    expect(screen.getByText("Focus timer")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("Progress")).toBeInTheDocument();
  });

  it("calls onSelectTab when an inactive nav item is clicked", () => {
    const handleSelect = vi.fn();
    render(
      <AuthProvider>
        <Sidebar currentTab="dashboard" onSelectTab={handleSelect} />
      </AuthProvider>
    );

    const plannerBtn = screen.getByText("Revision planner");
    fireEvent.click(plannerBtn);
    expect(handleSelect).toHaveBeenCalledWith("planner");
  });

  it("renders sync status and sign out button in footer", () => {
    render(
      <AuthProvider>
        <Sidebar currentTab="dashboard" onSelectTab={() => {}} />
      </AuthProvider>
    );

    expect(screen.getByText("Your progress is saved on this device")).toBeInTheDocument();
    expect(screen.getByText("Sign out")).toBeInTheDocument();
  });
});
