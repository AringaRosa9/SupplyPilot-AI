import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "./button";

describe("Button", () => {
  it("preserves native button semantics", () => {
    render(<Button type="button">创建活动</Button>);
    expect(screen.getByRole("button", { name: "创建活动" })).toHaveAttribute("type", "button");
  });
});
