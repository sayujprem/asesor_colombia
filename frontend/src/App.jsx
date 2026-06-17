import { useState } from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Features from "./components/Features";
import Footer from "./components/Footer";
import Chat from "./components/Chat";

export default function App() {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />
      <main>
        <Hero onOpenChat={() => setChatOpen(true)} />
        <Features onOpenChat={() => setChatOpen(true)} />
      </main>
      <Footer />
      <Chat isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </>
  );
}
