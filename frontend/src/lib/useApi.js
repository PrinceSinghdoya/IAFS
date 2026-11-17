import { useCallback, useEffect, useRef, useState } from "react";

import { api } from "./api";

/**
 * Small data-loading hook shared by the pages.
 *
 * - Re-fetches whenever `path` changes.
 * - Ignores stale responses (for example when the user changes a filter).
 * - Keeps `data` while reloading so the page does not flash empty.
 */
export function useApi(path, { skip = false } = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(Boolean(!skip && path));
  const [error, setError] = useState("");
  const requestRef = useRef(0);

  const load = useCallback(async () => {
    if (!path) {
      setLoading(false);
      return;
    }
    const requestId = ++requestRef.current;
    setLoading(true);
    setError("");
    try {
      const result = await api.get(path);
      if (requestId === requestRef.current) setData(result);
    } catch (err) {
      if (requestId === requestRef.current) setError(err.message || "Something went wrong");
    } finally {
      if (requestId === requestRef.current) setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    if (skip) {
      setLoading(false);
      return undefined;
    }
    load();
    return () => {
      // Invalidate this request when the path changes or the page unmounts.
      requestRef.current += 1;
    };
  }, [load, skip]);

  return { data, loading, error, reload: load, setData };
}

export function useDocumentTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} | IAFS School Learning` : "IAFS | Learning that adapts to every child";
  }, [title]);
}

/** Small helper for safe numeric percentages. */
export function numberOrNull(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}
