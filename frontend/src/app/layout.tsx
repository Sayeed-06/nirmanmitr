import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "NirmanMitr — BOQ Analysis & CPWD DSR Knowledge",
  description:
    "Instantly understand every BOQ item. Upload your Bill of Quantities, detect CPWD DSR items, and access structured knowledge cards with materials, execution steps, and specifications.",
  keywords: [
    "BOQ",
    "CPWD",
    "DSR",
    "Delhi Schedule of Rates",
    "quantity surveying",
    "civil engineering",
    "construction",
  ],
};

import { ClerkProvider } from "@clerk/nextjs";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body
          className={`${inter.variable} ${jetbrains.variable} font-sans`}
        >
          <Providers>{children}</Providers>
        </body>
      </html>
    </ClerkProvider>
  );
}
