import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "./components/Navigation";

export const metadata: Metadata = {
  title: "AI Discovery Engine",
  description: "Analysis of retrieval failures.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#FAFAFA] flex flex-col">
        <Navigation />
        <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-6 sm:px-6 md:px-8 md:py-10">
          {children}
        </main>
      </body>
    </html>
  );
}
