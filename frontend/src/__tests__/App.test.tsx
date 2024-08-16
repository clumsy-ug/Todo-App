import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "../App";

// モックの設定
vi.mock("react-hot-toast", () => ({
    default: {
        success: vi.fn(),
        error: vi.fn(),
    },
    Toaster: vi.fn(),
}));

vi.mock("react-icons/fa", () => ({
    FaTrash: vi.fn(() => null),
    FaEdit: vi.fn(() => null),
    FaPlus: vi.fn(() => null),
    FaSignOutAlt: vi.fn(() => null),
}));

// APIのモック
global.fetch = vi.fn();

describe("App Component", () => {
    beforeEach(() => {
        localStorage.clear();
        (global.fetch as any).mockClear();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    it("adds a new todo", async () => {
        localStorage.setItem("token", "fake_token");
        localStorage.setItem("username", "testuser");

        /* fetchのモックを設定 */
        (global.fetch as any)
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve([]), // テスト開始時はtodoリストが空なことを保証
            })
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ id: 1, content: "New todo" }),
            });

        render(<App />);

        await waitFor(() => {
            fireEvent.change(screen.getByPlaceholderText("新しいTodoを入力"), {
                target: { value: "New todo" },
            });
            fireEvent.click(screen.getByText("登録"));
        });

        await waitFor(() => {
            expect(screen.getByText("New todo")).toBeInTheDocument();
        });
    });

    it("deletes a todo", async () => {
        localStorage.setItem("token", "fake_token");
        localStorage.setItem("username", "testuser");

        /* fetchのモックを設定 */
        // 各呼び出し（mockResolvedValueOnce）は非同期で、実際のAPI呼び出しに対応する
        // そのためこのfetchのモック部分で削除処理自体は書いていないが、削除処理が成功した瞬間、そして成功した後はどのようなものを返すかを書いている
        (global.fetch as any)
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve([{ id: 1, content: "Test todo" }]), // 初期Todoリストの取得
            })
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ id: 1, content: "Test todo" }), // 削除操作の成功レスポンス
            })
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve([]), // 削除操作後の更新されたTodoリストの取得(=空)
            });

        render(<App />);

        await waitFor(() => {
            expect(screen.getByText("Test todo")).toBeInTheDocument();
        });

        fireEvent.click(screen.getAllByRole("button")[2]); // Delete button

        await waitFor(() => {
            expect(screen.queryByText("Test todo")).not.toBeInTheDocument();
        });
    });

    it("updates a todo", async () => {
        localStorage.setItem("token", "fake_token");
        localStorage.setItem("username", "testuser");

        (global.fetch as any)
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve([{ id: 1, content: "Test todo" }]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ id: 1, content: "Updated todo" }),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: () =>
                    Promise.resolve([{ id: 1, content: "Updated todo" }]),
            });

        render(<App />);

        await waitFor(() => {
            expect(screen.getByText("Test todo")).toBeInTheDocument();
        });

        global.prompt = vi.fn(() => "Updated todo");
        fireEvent.click(screen.getAllByRole("button")[1]); // Edit button

        await waitFor(() => {
            expect(screen.getByText("Updated todo")).toBeInTheDocument();
        });
    });

    it("renders login form when not logged in", () => {
        render(<App />);
        expect(
            screen.getByRole("heading", { name: "Login" })
        ).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Username")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
    });

    it("handles successful login", async () => {
        (global.fetch as any).mockImplementation((url: any) => {
            if (url.includes("/login")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ access_token: "fake_token" }),
                });
            } else if (url.includes("/todos")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([]), // 空のTodoリストを返す
                });
            }
        });

        render(<App />);
        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });
        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "password" },
        });
        fireEvent.click(screen.getByRole("button", { name: "Login" }));

        await waitFor(() => {
            expect(
                screen.getByText("Welcome,", { exact: false })
            ).toBeInTheDocument();
            expect(
                screen.getByText("testuser", { exact: false })
            ).toBeInTheDocument();
        });
    });

    it("renders todos after successful login", async () => {
        localStorage.setItem("token", "fake_token");
        localStorage.setItem("username", "testuser");

        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: () =>
                Promise.resolve([
                    { id: 1, content: "Test todo 1" },
                    { id: 2, content: "Test todo 2" },
                ]),
        });

        render(<App />);

        await waitFor(() => {
            expect(screen.getByText("Test todo 1")).toBeInTheDocument();
            expect(screen.getByText("Test todo 2")).toBeInTheDocument();
        });
    });

    it("handles failed login", async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: false,
            json: () => Promise.resolve({ msg: "Bad username or password" }),
        });

        render(<App />);
        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "wronguser" },
        });
        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "wrongpass" },
        });
        fireEvent.click(screen.getByRole("button", { name: "Login" }));

        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: "Login" })
            ).toBeInTheDocument();
        });
    });

    it("logs out successfully", async () => {
        localStorage.setItem("token", "fake_token");
        localStorage.setItem("username", "testuser");

        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve([]),
        });

        render(<App />);

        await waitFor(() => {
            expect(
                screen.getByText("Welcome,", { exact: false })
            ).toBeInTheDocument();
            expect(
                screen.getByText("testuser", { exact: false })
            ).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText("Logout"));

        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: "Login" })
            ).toBeInTheDocument();
        });
    });

    it("switches to registration form", () => {
        render(<App />);
        fireEvent.click(screen.getByText("Need to register?"));
        expect(
            screen.getByRole("heading", { name: "Register" })
        ).toBeInTheDocument();
    });

    it("handles successful registration", async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ msg: "Registration successful" }),
        });

        render(<App />);
        fireEvent.click(screen.getByText("Need to register?"));
        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "newuser" },
        });
        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "newpass" },
        });
        fireEvent.click(screen.getByRole("button", { name: "Register" }));

        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: "Login" })
            ).toBeInTheDocument();
        });
    });
});
