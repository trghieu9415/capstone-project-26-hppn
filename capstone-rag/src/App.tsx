import { Sidebar } from "@/components/layout/Sidebar";
import { GlobalDialogs } from "@/components/features/management/GlobalDialogs";
import { MainArea } from "@/components/layout/MainArea";
import { ToastContainer } from "./components/shared/ToastContainer";

export default function App() {
  return (
    <div className="flex h-screen bg-white overflow-hidden font-sans">
      <Sidebar />
      <MainArea />
      <GlobalDialogs />
      <ToastContainer />
    </div>
  );
}
