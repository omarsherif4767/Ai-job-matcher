import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "../components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "A Job in AI Era — Career Intelligence Platform",
  description: "AI-powered career platform: resume parsing, job matching, cover letter generation, interview coaching, and skill gap analysis.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className} style={{ margin: 0, background: "#0a0d14", color: "#e2e8f0" }}>
        <div style={{ display: "flex" }}>
          <Sidebar />
          <main style={{ marginLeft: "220px", flex: 1, minHeight: "100vh", padding: "32px" }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
