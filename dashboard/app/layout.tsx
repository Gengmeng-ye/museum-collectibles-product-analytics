import type { Metadata } from 'next';
import { Archivo } from 'next/font/google';
import './globals.css';

const archivo = Archivo({
  variable: '--font-body',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'Museum Blind Box Consumer Insights',
  description:
    'Product assortment, customer voice, and model diagnostics for museum-themed blind boxes.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${archivo.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
