import "./styles.css";
import "./desktop.css";
import "./desktop-fix.css";
export const metadata = {title: "Memento", description: "Your calm personal agent"};
export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) { return <html lang="en"><body>{children}</body></html>; }
