import { render, screen } from "@testing-library/react";
import Spinner from "../components/Spinner";

describe("Spinner Component", () => {
    it("renders the spinner and loading text", () => {
        render(<Spinner />);

        // "Loading..." テキストが存在することを確認
        expect(screen.getByText("Loading...")).toBeInTheDocument();

        // スピナーのdiv要素が存在することを確認
        const spinnerElement = screen.getByRole("status");
        expect(spinnerElement).toHaveClass("spinner");
    });
});
