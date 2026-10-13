import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "../src/App";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

test("renders navigation and demo mode control", async () => {
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/incidents")) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            items: [],
            total: 0,
            page: 1,
          }),
          {
            status: 200,
            headers: {
              "Content-Type": "application/json",
            },
          },
        ),
      );
    }

    if (url.includes("/devices")) {
      return Promise.resolve(
        new Response(JSON.stringify([]), {
          status: 200,
          headers: {
            "Content-Type": "application/json",
          },
        }),
      );
    }

    if (url.includes("/diagnostics/system")) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            device_id: "demo-device",
            hostname: "demo-workstation",
            os_name: "Linux",
            os_version: "Demo",
            architecture: "x86_64",
            uptime_seconds: 86400,
            cpu_percent: 18.5,
            memory_total_bytes: 17179869184,
            memory_available_bytes: 9663676416,
            disks: [],
            collected_at: "2026-10-13T12:00:00Z",
            results: [],
          }),
          {
            status: 200,
            headers: {
              "Content-Type": "application/json",
            },
          },
        ),
      );
    }

    return Promise.resolve(
      new Response(
        JSON.stringify({
          error: {
            message: "Unexpected test request",
          },
        }),
        {
          status: 404,
          headers: {
            "Content-Type": "application/json",
          },
        },
      ),
    );
  });

  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  expect(
    screen.getByRole("button", { name: "Overview" }),
  ).toBeInTheDocument();

  expect(
    screen.getByRole("button", { name: "Diagnostics" }),
  ).toBeInTheDocument();

  expect(
    screen.getByRole("button", { name: "Incidents" }),
  ).toBeInTheDocument();

  expect(
    screen.getByLabelText("Demo mode"),
  ).toBeInTheDocument();

  expect(
    await screen.findByText("demo-workstation"),
  ).toBeInTheDocument();

  expect(fetchMock).toHaveBeenCalled();
});
