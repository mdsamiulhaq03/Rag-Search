import type { Metadata } from "next";
import { Literata, Schibsted_Grotesk } from "next/font/google";

import { THEME_INIT_SCRIPT } from "@/lib/theme";
import "./globals.css";

const schibsted = Schibsted_Grotesk({ variable: "--font-schibsted", subsets: ["latin"] });
const literata = Literata({ variable: "--font-literata", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Refer",
  description: "Refer: answers from your company docs, with the evidence highlighted.",
  applicationName: "Refer",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    // suppressHydrationWarning: the theme script sets data-theme on <html> before React hydrates.
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className={`${schibsted.variable} ${literata.variable} font-sans antialiased`}>{children}</body>
    </html>
  );
}
