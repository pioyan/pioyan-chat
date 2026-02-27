/**
 * Tests for MarkdownContent component
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import MarkdownContent from "@/components/MarkdownContent";

describe("MarkdownContent", () => {
  it("renders plain text", () => {
    render(<MarkdownContent content="Hello, world!" />);
    expect(screen.getByText("Hello, world!")).toBeInTheDocument();
  });

  it("renders bold text", () => {
    render(<MarkdownContent content="This is **bold** text" />);
    const strong = screen.getByText("bold");
    expect(strong.tagName).toBe("STRONG");
  });

  it("renders italic text", () => {
    render(<MarkdownContent content="This is *italic* text" />);
    const em = screen.getByText("italic");
    expect(em.tagName).toBe("EM");
  });

  it("renders inline code", () => {
    render(<MarkdownContent content="Use `console.log()` here" />);
    const code = screen.getByText("console.log()");
    expect(code.tagName).toBe("CODE");
  });

  it("renders code blocks", () => {
    render(
      <MarkdownContent content={'```\nconst x = 1;\n```'} />,
    );
    const code = screen.getByText("const x = 1;");
    expect(code.tagName).toBe("CODE");
    expect(code.closest("pre")).toBeInTheDocument();
  });

  it("renders unordered lists", () => {
    render(<MarkdownContent content={"- item one\n- item two"} />);
    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(2);
  });

  it("renders links", () => {
    render(
      <MarkdownContent content="Visit [example](https://example.com)" />,
    );
    const link = screen.getByRole("link", { name: "example" });
    expect(link).toHaveAttribute("href", "https://example.com");
  });

  it("renders headings", () => {
    render(<MarkdownContent content="## Section Title" />);
    expect(
      screen.getByRole("heading", { level: 2 }),
    ).toHaveTextContent("Section Title");
  });

  it("renders GFM strikethrough", () => {
    render(<MarkdownContent content="This is ~~deleted~~ text" />);
    const del = screen.getByText("deleted");
    expect(del.tagName).toBe("DEL");
  });

  it("renders GFM tables", () => {
    const table = "| Name | Age |\n| --- | --- |\n| Alice | 30 |";
    render(<MarkdownContent content={table} />);
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
  });
});
