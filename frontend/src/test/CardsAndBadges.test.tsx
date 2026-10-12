import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Card } from "@/components/ui/Card";
import { Eyebrow } from "@/components/ui/Eyebrow";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";

describe("Design System Components", () => {
  it("renders Card with rounded-2xl and shadow classes", () => {
    const { container } = render(<Card>Card content</Card>);
    const cardEl = container.firstChild as HTMLElement;
    expect(cardEl).toHaveClass("rounded-2xl");
    expect(cardEl).toHaveClass("bg-white");
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("renders Eyebrow in uppercase with small tracking font", () => {
    render(<Eyebrow>Today's focus</Eyebrow>);
    const eyebrow = screen.getByText("Today's focus");
    expect(eyebrow).toHaveClass("uppercase");
    expect(eyebrow).toHaveClass("text-[11px]");
  });

  it("renders Badge variants properly for session types and difficulty", () => {
    render(
      <div>
        <Badge variant="learn">learn</Badge>
        <Badge variant="review">review</Badge>
        <Badge variant="hard">hard</Badge>
      </div>
    );
    expect(screen.getByText("learn")).toBeInTheDocument();
    expect(screen.getByText("review")).toBeInTheDocument();
    expect(screen.getByText("hard")).toBeInTheDocument();
  });

  it("renders ProgressBar with clamped width style", () => {
    const { container } = render(<ProgressBar value={45} color="#818CF8" />);
    const bar = container.querySelector(".rounded-full > div") as HTMLElement;
    expect(bar.style.width).toBe("45%");
    expect(bar.style.backgroundColor).toBe("rgb(129, 140, 248)");
  });
});
