/* eslint-disable react-refresh/only-export-components */
import React, { Suspense, lazy } from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider, Outlet, Navigate } from "react-router-dom";
import Topbar from "./modules/components/Topbar";
import AuthProvider from "./modules/auth/AuthProvider";
import { ElectionProvider } from "./modules/election/context/ElectionContext";
import Private from "./modules/components/Private";
import RequireAdmin from "./modules/components/RequireAdmin";
import { ToastProvider } from "./modules/ui/Toast";
import "./index.css";
import "./styles/election.css";


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
      { path: "/ballot", element: <Private><Suspense fallback={null}><BallotPage /></Suspense></Private> },
      { path: "/results", element: <Private><Suspense fallback={null}><OfficerResults /></Suspense></Private> },
      {
        path: "/admin/election",
        element: (
          <Private>
            <RequireAdmin>
              <Suspense fallback={null}><AdminElectionPage /></Suspense>
            </RequireAdmin>
          </Private>
        ),
      },
      { path: "/elections/:id/ballot", element: <Navigate to="/ballot" replace /> },
      { path: "/elections/:id/results", element: <Navigate to="/results" replace /> },
      { path: "*", element: <div style={{ padding: 16 }}>Not found</div> }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ToastProvider>
      <AuthProvider>
        <ElectionProvider>
          <RouterProvider router={router} />
        </ElectionProvider>
      </AuthProvider>
    </ToastProvider>
  </React.StrictMode>
);
