import React, { Suspense, lazy } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { createBrowserRouter, RouterProvider, Outlet, Navigate } from "react-router-dom";
import Topbar from "./modules/components/Topbar";
import { AuthProvider } from "./modules/auth/AuthProvider";
import { ElectionProvider } from "./modules/election/context/ElectionContext";
import Private from "./modules/components/Private";
import RequireAdmin from "./modules/components/RequireAdmin";
import { ToastProvider } from "./modules/ui/Toast";

const LoginPage = lazy(() => import("./modules/pages/LoginPage"));
const BallotPage = lazy(() => import("./modules/pages/BallotPage"));
const OfficerResults = lazy(() => import("./modules/pages/OfficerResults"));
const AdminElectionPage = lazy(() => import("./modules/election/pages/AdminElectionPage"));

function Shell() {
  return (
    <>
      <Topbar />
      <main style={{ maxWidth: 1100, margin: "0 auto", padding: "16px" }}>
        <Outlet />
      </main>
    </>
  );
}

const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { path: "/", element: <Navigate to="/ballot" replace /> },
      { path: "/login", element: <Suspense fallback={null}><LoginPage /></Suspense> },
      {
        element: <Private />,
        children: [
          { path: "/ballot", element: <Suspense fallback={null}><BallotPage /></Suspense> },
          { path: "/results", element: <Suspense fallback={null}><OfficerResults /></Suspense> },
          {
            element: <RequireAdmin />,
            children: [
              { path: "/admin/election", element: <Suspense fallback={null}><AdminElectionPage /></Suspense> }
            ]
          }
        ]
      },
      { path: "/elections/:id/ballot", element: <Navigate to="/ballot" replace /> },
      { path: "/elections/:id/results", element: <Navigate to="/results" replace /> },
      { path: "*", element: <div style={{ padding: 16 }}>Not found</div> }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <ElectionProvider>
        <ToastProvider>
          <RouterProvider router={router} />
        </ToastProvider>
      </ElectionProvider>
    </AuthProvider>
  </React.StrictMode>
);
