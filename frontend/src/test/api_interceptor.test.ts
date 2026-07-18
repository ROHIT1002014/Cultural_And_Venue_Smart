import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

// Unmock api if previously mocked
vi.unmock("@/services/api");

import api from "@/services/api";

describe("api.ts interceptors", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it("attaches Authorization header if access_token exists", async () => {
    localStorage.setItem("access_token", "test-access-token");

    // Extract request interceptor handlers
    // @ts-expect-error accessing internal handlers for testing
    const reqHandlers = api.interceptors.request.handlers;
    const fulfilledHandler = reqHandlers[0]?.fulfilled;
    expect(fulfilledHandler).toBeDefined();

    const config: InternalAxiosRequestConfig = {
      headers: new axios.AxiosHeaders(),
    } as InternalAxiosRequestConfig;

    const resConfig = await fulfilledHandler(config);
    expect(resConfig.headers.Authorization).toBe("Bearer test-access-token");
  });

  it("request interceptor error handler rejects promise", async () => {
    // @ts-expect-error accessing internal handlers for testing
    const reqHandlers = api.interceptors.request.handlers;
    const rejectedHandler = reqHandlers[0]?.rejected;
    expect(rejectedHandler).toBeDefined();

    const err = new Error("Request error");
    await expect(rejectedHandler(err)).rejects.toThrow("Request error");
  });

  it("response interceptor success handler passes response through", async () => {
    // @ts-expect-error accessing internal handlers for testing
    const resHandlers = api.interceptors.response.handlers;
    const fulfilledHandler = resHandlers[0]?.fulfilled;
    expect(fulfilledHandler).toBeDefined();

    const response = { data: "success", status: 200 };
    const res = await fulfilledHandler(response);
    expect(res).toEqual(response);
  });

  it("response interceptor refreshes token on 401 and retries original request", async () => {
    localStorage.setItem("refresh_token", "old-refresh-token");
    const postSpy = vi.spyOn(axios, "post").mockResolvedValueOnce({
      data: { access_token: "new-access", refresh_token: "new-refresh" },
    });

    const originalAdapter = api.defaults.adapter;
    const adapterMock = vi.fn().mockResolvedValue({
      data: "retried-data",
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });
    api.defaults.adapter = adapterMock;

    // @ts-expect-error accessing internal handlers for testing
    const resHandlers = api.interceptors.response.handlers;
    const rejectedHandler = resHandlers[0]?.rejected;

    const error: AxiosError = {
      isAxiosError: true,
      toJSON: () => ({}),
      name: "AxiosError",
      message: "401 Unauthorized",
      response: {
        status: 401,
        statusText: "Unauthorized",
        headers: {},
        config: {} as InternalAxiosRequestConfig,
        data: {},
      },
      config: {
        headers: new axios.AxiosHeaders(),
      } as InternalAxiosRequestConfig,
    };

    const res = await rejectedHandler(error);

    expect(postSpy).toHaveBeenCalledWith(expect.stringContaining("/auth/refresh"), {
      refresh_token: "old-refresh-token",
    });
    expect(adapterMock).toHaveBeenCalled();
    expect(res.data).toBe("retried-data");
    expect(localStorage.getItem("access_token")).toBe("new-access");
    expect(localStorage.getItem("refresh_token")).toBe("new-refresh");
    expect(error.config?.headers?.Authorization).toBe("Bearer new-access");

    api.defaults.adapter = originalAdapter;
  });

  it("response interceptor redirects to login on failed refresh", async () => {
    localStorage.setItem("refresh_token", "invalid-refresh");
    vi.spyOn(axios, "post").mockRejectedValueOnce(new Error("Refresh failed"));

    const originalLocation = window.location;
    // @ts-expect-error mock window.location
    delete window.location;
    window.location = { ...originalLocation, href: "" };

    // @ts-expect-error accessing internal handlers for testing
    const resHandlers = api.interceptors.response.handlers;
    const rejectedHandler = resHandlers[0]?.rejected;

    const error: AxiosError = {
      isAxiosError: true,
      toJSON: () => ({}),
      name: "AxiosError",
      message: "401 Unauthorized",
      response: {
        status: 401,
        statusText: "Unauthorized",
        headers: {},
        config: {} as InternalAxiosRequestConfig,
        data: {},
      },
      config: {
        headers: new axios.AxiosHeaders(),
      } as InternalAxiosRequestConfig,
    };

    await expect(rejectedHandler(error)).rejects.toThrow("Refresh failed");
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
    expect(window.location.href).toBe("/login");

    window.location = originalLocation;
  });

  it("response interceptor rejects non-401 or already retried errors immediately", async () => {
    // @ts-expect-error accessing internal handlers for testing
    const resHandlers = api.interceptors.response.handlers;
    const rejectedHandler = resHandlers[0]?.rejected;

    const error400: AxiosError = {
      isAxiosError: true,
      toJSON: () => ({}),
      name: "AxiosError",
      message: "400 Bad Request",
      response: {
        status: 400,
        statusText: "Bad Request",
        headers: {},
        config: {} as InternalAxiosRequestConfig,
        data: {},
      },
      config: {} as InternalAxiosRequestConfig,
    };

    await expect(rejectedHandler(error400)).rejects.toEqual(error400);
  });
});
