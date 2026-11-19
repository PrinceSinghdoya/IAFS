import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  Camera,
  CameraOff,
  CheckCircle2,
  Clock3,
  Info,
  Loader2,
  RefreshCw,
  Save,
  ScanFace,
  ShieldCheck,
  Video,
} from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader } from "../components/Loading";
import { PageHeader } from "../components/ui";
import { api } from "../lib/api";
import { isAttentiveFrame, measureAttention } from "../lib/attention";
import { formatDate, secondsToClock } from "../lib/format";

const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite";
const WASM_URL =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.35/wasm";

const EMPTY_STATS = { total: 0, face: 0, centered: 0, attention: 0 };

function indicatorFor(score) {
  if (score >= 75) return "Face visible and centred";
  if (score >= 45) return "Partly visible";
  return "Low signal";
}

function indicatorClass(indicator) {
  if (indicator === "Face visible and centred") {
    return "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200";
  }
  if (indicator === "Partly visible") {
    return "bg-amber-50 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200";
  }
  return "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200";
}

export default function CameraPage() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const detectorRef = useRef(null);
  const loopRef = useRef(null);
  const timerRef = useRef(null);
  const startTimeRef = useRef(null);
  const lastVideoTimeRef = useRef(-1);
  const statsRef = useRef({ ...EMPTY_STATS });
  const cameraActiveRef = useRef(false);
  const mountedRef = useRef(true);

  const [phase, setPhase] = useState("idle"); // idle | requesting | streaming
  const [modelStatus, setModelStatus] = useState("idle"); // idle | loading | ready | unavailable
  const [modelMessage, setModelMessage] = useState("");
  const [cameraError, setCameraError] = useState("");
  const [faceDetected, setFaceDetected] = useState(false);
  const [headCentered, setHeadCentered] = useState(false);
  const [stats, setStats] = useState({ ...EMPTY_STATS });
  const [elapsed, setElapsed] = useState(0);
  const [saving, setSaving] = useState(false);
  const [savedRecord, setSavedRecord] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const [focusLevel, setFocusLevel] = useState(3);
  const [minutes, setMinutes] = useState(10);
  const [manualError, setManualError] = useState("");
  const [savingManual, setSavingManual] = useState(false);

  const faceRatio = stats.total ? (stats.face / stats.total) * 100 : 0;
  const centeredRatio = stats.total ? (stats.centered / stats.total) * 100 : 0;
  const liveScore = Math.round(faceRatio * 0.7 + centeredRatio * 0.3);
  const liveIndicator =
    stats.total < 5 ? "Collecting signal" : indicatorFor(liveScore);
  const attention = measureAttention(stats);
  const liveAttention = stats.total < 5 ? "Collecting signal" : attention.indicator;

  function applySaved(data) {
    setSavedRecord(data.record);
    setHistory((current) => [data.record, ...current].slice(0, 10));
  }

  useEffect(() => {
    let active = true;
    api
      .get("/engagement/latest")
      .then((data) => {
        if (!active) return;
        setHistory(data.history || []);
      })
      .catch(() => {})
      .finally(() => active && setHistoryLoading(false));
    return () => {
      active = false;
    };
  }, []);

  // The <video> element only exists while streaming, so attach the stream
  // after React has rendered it (not before setPhase).
  useEffect(() => {
    if (phase !== "streaming") return;
    const video = videoRef.current;
    const stream = streamRef.current;
    if (!video || !stream) return;
    video.srcObject = stream;
    video.play().catch(() => {});
  }, [phase]);

  // Stop hardware and timers when leaving the page. Nothing is uploaded.
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      cameraActiveRef.current = false;
      clearInterval(loopRef.current);
      clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((track) => track.stop());
      detectorRef.current?.close?.();
    };
  }, []);

  function startStats() {
    statsRef.current = { ...EMPTY_STATS };
    setStats({ ...EMPTY_STATS });
    setElapsed(0);
    setFaceDetected(false);
    setHeadCentered(false);
  }

  async function setupDetector() {
    setModelStatus("loading");
    setModelMessage("");
    try {
      const { FilesetResolver, FaceDetector } = await import("@mediapipe/tasks-vision");
      const vision = await FilesetResolver.forVisionTasks(WASM_URL);

      let detector;
      try {
        detector = await FaceDetector.createFromOptions(vision, {
          baseOptions: { modelAssetPath: MODEL_URL, delegate: "GPU" },
          runningMode: "VIDEO",
          minDetectionConfidence: 0.55,
        });
      } catch {
        // GPU is not available on every laptop; CPU is a reliable fallback.
        detector = await FaceDetector.createFromOptions(vision, {
          baseOptions: { modelAssetPath: MODEL_URL, delegate: "CPU" },
          runningMode: "VIDEO",
          minDetectionConfidence: 0.55,
        });
      }

      if (!mountedRef.current || !cameraActiveRef.current) {
        detector.close?.();
        return;
      }

      detectorRef.current = detector;
      setModelStatus("ready");
      startDetectionLoop();
    } catch {
      if (!mountedRef.current) return;
      setModelStatus("unavailable");
      setModelMessage(
        "The face-detection model could not load. It needs an internet connection the first time. The live preview still works, and you can log a manual focus check-in below."
      );
    }
  }

  function startDetectionLoop() {
    clearInterval(loopRef.current);
    lastVideoTimeRef.current = -1;

    loopRef.current = setInterval(() => {
      const detector = detectorRef.current;
      const video = videoRef.current;
      if (!detector || !video || video.readyState < 2) return;
      if (video.currentTime === lastVideoTimeRef.current) return;
      lastVideoTimeRef.current = video.currentTime;

      try {
        const result = detector.detectForVideo(video, performance.now());
        const detection = result.detections?.[0];
        const next = statsRef.current;
        next.total += 1;

        if (detection) {
          next.face += 1;
          const box = detection.boundingBox;
          const nose = detection.keypoints?.[2];
          let centered = false;
          if (box?.width && nose) {
            const centerX = box.originX + box.width / 2;
            centered = Math.abs(nose.x - centerX) / (box.width / 2) < 0.35;
          }
          if (centered) next.centered += 1;
          if (isAttentiveFrame(detection)) next.attention += 1;
          setFaceDetected(true);
          setHeadCentered(centered);
        } else {
          setFaceDetected(false);
          setHeadCentered(false);
        }

        if (mountedRef.current) setStats({ ...next });
      } catch {
        // A single failed frame should not stop the session.
      }
    }, 350);
  }

  async function startCamera() {
    setCameraError("");
    setSavedRecord(null);
    setModelStatus("idle");
    setModelMessage("");
    startStats();

    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError("This browser does not support camera access. Use a recent Chrome, Edge or Firefox build.");
      return;
    }

    setPhase("requesting");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      });

      streamRef.current = stream;
      cameraActiveRef.current = true;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => {});
      }

      setPhase("streaming");
      startTimeRef.current = Date.now();
      timerRef.current = setInterval(() => {
        if (mountedRef.current && startTimeRef.current) {
          setElapsed(Math.floor((Date.now() - startTimeRef.current) / 1000));
        }
      }, 1000);

      setupDetector();
    } catch (err) {
      cameraStreamStop();
      setPhase("idle");
      if (err?.name === "NotAllowedError" || err?.name === "SecurityError") {
        setCameraError(
          "Camera permission was denied. You can allow it in the browser site settings, or simply use the manual focus check-in below. All other features work without the camera."
        );
      } else if (err?.name === "NotFoundError") {
        setCameraError("No camera was found on this device. The manual focus check-in is available below.");
      } else {
        setCameraError("The camera could not be started. You can continue using the manual focus check-in.");
      }
    }
  }

  function cameraStreamStop() {
    cameraActiveRef.current = false;
    clearInterval(loopRef.current);
    clearInterval(timerRef.current);
    loopRef.current = null;
    timerRef.current = null;

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;

    detectorRef.current?.close?.();
    detectorRef.current = null;
    lastVideoTimeRef.current = -1;
  }

  async function endSession({ save = true } = {}) {
    const sessionStats = { ...statsRef.current };
    const seconds = Math.max(1, Math.floor((Date.now() - (startTimeRef.current || Date.now())) / 1000));

    cameraStreamStop();
    setPhase("idle");
    setFaceDetected(false);

    if (!save) return;

    if (sessionStats.total < 5) {
      setCameraError(
        "Not enough frames were analysed to save a session. Keep the camera on for a few seconds, or use the manual check-in."
      );
      return;
    }

    setSaving(true);
    setCameraError("");
    try {
      const data = await api.post("/engagement", {
        source: "camera",
        session_seconds: seconds,
        total_samples: sessionStats.total,
        face_detected_samples: sessionStats.face,
        head_centered_samples: sessionStats.centered,
        attentive_samples: sessionStats.attention,
      });
      applySaved(data);
    } catch (err) {
      setCameraError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function saveManual(event) {
    event.preventDefault();
    setSavingManual(true);
    setManualError("");
    try {
      const data = await api.post("/engagement", {
        source: "manual",
        session_seconds: Number(minutes) * 60,
        focus_level: Number(focusLevel),
      });
      applySaved(data);
    } catch (err) {
      setManualError(err.message);
    } finally {
      setSavingManual(false);
    }
  }

  if (historyLoading) return <SectionLoader label="Loading focus sessions..." />;

  const savedTone =
    (savedRecord && indicatorClass(savedRecord.indicator)) ||
    "bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-300";

  return (
    <div className="animate-fade-in">
      <PageHeader
        eyebrow="Optional focus check"
        title="Optional focus check"
        subtitle="A privacy-first, optional check. Your browser estimates attention from whether a face is present and roughly turned toward the camera. It never records, identifies or judges you."
        actions={
          <span className="chip bg-amber-50 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200">
            <ShieldCheck className="h-3.5 w-3.5" />
            Optional feature
          </span>
        }
      />

      {cameraError && (
        <Alert tone="error" className="mb-5">
          <div className="flex flex-wrap items-center gap-3">
            <span>{cameraError}</span>
            {phase === "idle" && (
              <button
                type="button"
                onClick={startCamera}
                className="font-semibold underline underline-offset-2"
              >
                Try again
              </button>
            )}
          </div>
        </Alert>
      )}

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <div className="space-y-5">
          {/* Consent / start */}
          {phase === "idle" && !savedRecord && (
            <div className="card overflow-hidden">
              <div className="flex flex-col items-center px-6 py-10 text-center">
                <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 dark:bg-primary-500/15 dark:text-primary-300">
                  <ScanFace className="h-8 w-8" />
                </span>
                <h2 className="mt-4 text-lg font-bold text-ink">
                  The camera check is optional
                </h2>
                <p className="mt-1.5 max-w-md text-sm leading-relaxed text-muted">
                  Nothing is enabled until you press the button below. Your browser
                  will ask for permission, and you can stop at any time.
                </p>

                <div className="mt-5 grid w-full max-w-2xl gap-3 text-left sm:grid-cols-3">
                  {[
                    {
                      icon: ShieldCheck,
                      title: "No recordings",
                      text: "Frames are processed in memory and discarded.",
                    },
                    {
                      icon: ScanFace,
                      title: "Face presence only",
                      text: "No recognition, identity or emotion detection.",
                    },
                    {
                      icon: CameraOff,
                      title: "Always optional",
                      text: "Every other feature works without it.",
                    },
                  ].map((item) => {
                    const Icon = item.icon;
                    return (
                      <div key={item.title} className="rounded-xl border border-line bg-surface-2/50 p-3.5">
                        <Icon className="h-4 w-4 text-primary-600" />
                        <p className="mt-1.5 text-xs font-semibold text-ink">{item.title}</p>
                        <p className="mt-0.5 text-[10px] leading-relaxed text-muted">{item.text}</p>
                      </div>
                    );
                  })}
                </div>

                <button type="button" onClick={startCamera} className="btn-primary mt-6">
                  <Camera className="h-4 w-4" />
                  Enable camera for this session
                </button>
                <p className="mt-2 text-[10px] text-muted">
                  Requires a laptop webcam or phone camera. Internet is needed once to
                  load the face-detection model.
                </p>
              </div>
            </div>
          )}

          {phase === "requesting" && (
            <div className="card flex flex-col items-center px-6 py-14 text-center">
              <Loader2 className="h-7 w-7 animate-spin text-primary-600" />
              <p className="mt-3 text-sm font-medium text-ink/85">Requesting camera permission...</p>
              <p className="mt-1 text-xs text-muted">Choose “Allow” in your browser.</p>
            </div>
          )}

          {phase === "streaming" && (
            <div className="card overflow-hidden">
              <div className="relative aspect-video w-full overflow-hidden bg-slate-900">
                <video
                  ref={videoRef}
                  className="h-full w-full -scale-x-100 object-cover"
                  autoPlay
                  muted
                  playsInline
                />

                {/* Live overlays */}
                <div className="absolute left-3 top-3 flex flex-wrap gap-2">
                  <span className="chip bg-black/50 text-white backdrop-blur">
                    <span className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-rose-400" />
                    LIVE · {secondsToClock(elapsed)}
                  </span>
                  <span
                    className={`chip backdrop-blur ${
                      faceDetected ? "bg-emerald-500/90 text-white" : "bg-amber-500/90 text-white"
                    }`}
                  >
                    {faceDetected ? "Face detected" : "No face detected"}
                  </span>
                </div>

                <div className="absolute bottom-3 left-3 right-3 flex flex-wrap items-center justify-between gap-2">
                  <span className="chip bg-black/50 text-white backdrop-blur">
                    <Video className="h-3.5 w-3.5" />
                    {headCentered ? "Head roughly centred" : faceDetected ? "Head off-centre" : "Waiting for a face"}
                  </span>
                  <span className="chip bg-black/50 text-white backdrop-blur">
                    {stats.total} frames · {Math.round(attention.score)}% attention
                  </span>
                </div>

                {modelStatus === "loading" && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/50 text-white backdrop-blur-sm">
                    <Loader2 className="h-6 w-6 animate-spin" />
                    <p className="mt-2 text-xs font-medium">Loading face detection...</p>
                  </div>
                )}
              </div>

              <div className="p-5">
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="rounded-xl bg-surface-2/60 p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">
                      Face visible
                    </p>
                    <p className="mt-1 text-xl font-bold text-ink">
                      {Math.round(faceRatio)}%
                    </p>
                  </div>
                  <div className="rounded-xl bg-surface-2/60 p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">
                      Head centred
                    </p>
                    <p className="mt-1 text-xl font-bold text-ink">
                      {Math.round(centeredRatio)}%
                    </p>
                  </div>
                  <div className="rounded-xl bg-primary-50/70 p-3 dark:bg-primary-500/10">
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-primary-700 dark:text-primary-200">
                      Attention estimate
                    </p>
                    <p className="mt-1 text-xl font-bold text-ink">
                      {Math.round(attention.score)}%
                    </p>
                    <p className="text-[10px] text-primary-700/80 dark:text-primary-200/80">
                      {liveAttention}
                    </p>
                  </div>
                  <div className="rounded-xl bg-surface-2/60 p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">
                      Focus indicator
                    </p>
                    <p className="mt-1 text-sm font-bold text-ink">{liveIndicator}</p>
                    <p className="text-[10px] text-muted">{liveScore}% signal</p>
                  </div>
                </div>

                {modelStatus === "unavailable" && (
                  <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-[11px] leading-relaxed text-amber-800 dark:bg-amber-500/10 dark:text-amber-200">
                    {modelMessage}
                  </p>
                )}

                <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                  <button
                    type="button"
                    onClick={() => endSession({ save: true })}
                    disabled={saving}
                    className="btn-primary flex-1"
                  >
                    {saving ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Saving session...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4" />
                        End session &amp; save
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => endSession({ save: false })}
                    className="btn-secondary"
                  >
                    <CameraOff className="h-4 w-4" />
                    Turn camera off
                  </button>
                </div>
                <p className="mt-2 text-center text-[10px] text-muted">
                  Only aggregate percentages and session length are sent to the
                  server. No frames leave your browser.
                </p>
              </div>
            </div>
          )}

          {/* Saved session */}
          {savedRecord && (
            <div className="card p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-500/15 dark:text-emerald-300">
                    <CheckCircle2 className="h-4 w-4" />
                  </span>
                  <div>
                    <p className="text-sm font-bold text-ink">Focus session saved</p>
                    <p className="text-[11px] text-muted">
                      {formatDate(savedRecord.created_at, { withTime: true })} ·{" "}
                      {savedRecord.source === "camera" ? "camera session" : "manual check-in"}
                    </p>
                  </div>
                </div>
                <span className={`chip ${savedTone}`}>{savedRecord.indicator}</span>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                <div className="rounded-lg bg-surface-2/60 p-3">
                  <p className="text-[10px] uppercase text-muted">Signal score</p>
                  <p className="mt-0.5 text-lg font-bold text-ink">
                    {savedRecord.engagement_score}%
                  </p>
                </div>
                <div className="rounded-lg bg-primary-50/70 p-3 dark:bg-primary-500/10">
                  <p className="text-[10px] uppercase text-primary-700 dark:text-primary-200">
                    Attention estimate
                  </p>
                  <p className="mt-0.5 text-lg font-bold text-ink">
                    {savedRecord.attention_score != null
                      ? `${savedRecord.attention_score}%`
                      : "—"}
                  </p>
                  <p className="text-[9px] text-primary-700/80 dark:text-primary-200/80">
                    {savedRecord.attention_indicator}
                  </p>
                </div>
                <div className="rounded-lg bg-surface-2/60 p-3">
                  <p className="text-[10px] uppercase text-muted">Session length</p>
                  <p className="mt-0.5 text-lg font-bold text-ink">
                    {Math.round((savedRecord.session_seconds || 0) / 60)} min
                  </p>
                </div>
                <div className="rounded-lg bg-surface-2/60 p-3">
                  <p className="text-[10px] uppercase text-muted">Face visible</p>
                  <p className="mt-0.5 text-lg font-bold text-ink">
                    {savedRecord.face_ratio != null ? `${savedRecord.face_ratio}%` : "—"}
                  </p>
                </div>
                <div className="rounded-lg bg-surface-2/60 p-3">
                  <p className="text-[10px] uppercase text-muted">Head centred</p>
                  <p className="mt-0.5 text-lg font-bold text-ink">
                    {savedRecord.head_centered_ratio != null
                      ? `${savedRecord.head_centered_ratio}%`
                      : "—"}
                  </p>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setSavedRecord(null);
                    startCamera();
                  }}
                  className="btn-secondary py-2 text-xs"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Start another session
                </button>
                <Link to="/feedback" className="btn-ghost py-2 text-xs">
                  View full feedback
                </Link>
              </div>
            </div>
          )}

          {/* Manual fallback */}
          <form onSubmit={saveManual} className="card p-5 sm:p-6">
            <div className="flex items-start gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-surface-2 text-muted">
                <Clock3 className="h-4 w-4" />
              </span>
              <div>
                <h2 className="text-sm font-bold text-ink">Manual focus check-in</h2>
                <p className="mt-0.5 text-xs leading-relaxed text-muted">
                  Prefer not to use the camera? Self-report a focused study session
                  instead. It is an optional private record and never changes your quiz results.
                </p>
              </div>
            </div>

            {manualError && <Alert tone="error" className="mt-4">{manualError}</Alert>}

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="focus" className="label">
                  How attentive did you feel? ({focusLevel}/5)
                </label>
                <input
                  id="focus"
                  type="range"
                  min="1"
                  max="5"
                  step="1"
                  value={focusLevel}
                  onChange={(event) => setFocusLevel(event.target.value)}
                  className="w-full accent-primary-600"
                />
                <div className="mt-1 flex justify-between text-[10px] text-muted">
                  <span>Distracted</span>
                  <span>Very attentive</span>
                </div>
              </div>
              <div>
                <label htmlFor="minutes" className="label">
                  Study duration (minutes)
                </label>
                <input
                  id="minutes"
                  type="number"
                  min="1"
                  max="120"
                  value={minutes}
                  onChange={(event) => setMinutes(event.target.value)}
                  className="input"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={savingManual}
              className="btn-secondary mt-4 w-full sm:w-auto"
            >
              {savingManual ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4" />
                  Save manual check-in
                </>
              )}
            </button>
          </form>
        </div>

        {/* Sidebar */}
        <aside className="space-y-5">
          <div className="card p-5">
            <h2 className="inline-flex items-center gap-2 text-sm font-bold text-ink">
              <ScanFace className="h-4 w-4 text-primary-600" />
              What is measured
            </h2>
            <ul className="mt-3 space-y-2.5 text-[11px] leading-relaxed text-ink/75">
              <li className="flex gap-2">
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
                Whether a face is visible in the frame.
              </li>
              <li className="flex gap-2">
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
                Whether the head is roughly centred (basic orientation signal).
              </li>
              <li className="flex gap-2">
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
                An attention estimate: the share of frames where the face was
                visible and roughly facing the camera.
              </li>
              <li className="flex gap-2">
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
                A combined focus indicator from the camera signals.
              </li>
            </ul>
            <div className="mt-3 rounded-lg bg-rose-50 p-3 text-[10px] leading-relaxed text-rose-700 dark:bg-rose-500/10 dark:text-rose-200">
              <span className="font-bold">Not measured:</span> emotions,
              boredom, identity, facial recognition or real understanding. The
              attention estimate is only a privacy-safe proxy from face position;
              a still face can simply mean deep concentration.
            </div>
          </div>

          <div className="card p-5">
            <h2 className="text-sm font-bold text-ink">Recent focus sessions</h2>
            {history.length === 0 ? (
              <p className="mt-2 text-xs leading-relaxed text-muted">
                No sessions yet. Camera and manual sessions both appear here.
              </p>
            ) : (
              <div className="mt-3 space-y-2.5">
                {history.slice(0, 5).map((record) => (
                  <div
                    key={record.id}
                    className="flex items-center justify-between gap-2 rounded-lg border border-line px-3 py-2.5"
                  >
                    <div>
                      <p className="text-xs font-semibold text-ink">
                        {record.attention_score != null
                          ? `${record.attention_score}% attention`
                          : "Attention —"}{" "}
                        · {record.engagement_score}% focus
                      </p>
                      <p className="text-[10px] text-muted">
                        {record.source === "camera" ? "Camera" : "Manual"} ·{" "}
                        {formatDate(record.created_at, { withTime: true })}
                      </p>
                    </div>
                    <span className={`chip ${indicatorClass(record.indicator)}`}>
                      {record.indicator}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-line bg-surface p-4">
            <p className="flex items-center gap-1.5 text-[11px] font-bold text-ink/85">
              <ShieldCheck className="h-4 w-4 text-emerald-500" />
              Privacy statement
            </p>
            <p className="mt-1.5 text-[10px] leading-relaxed text-muted">
              Video frames are never uploaded or saved. Only counts and
              percentages — including the attention estimate — are stored,
              linked to your student ID, so you can see your own history. It is
              never used for grades.
            </p>
          </div>

          <div className="flex items-start gap-2 rounded-xl bg-blue-50 px-3 py-2.5 text-[10px] leading-relaxed text-blue-700 dark:bg-blue-500/10 dark:text-blue-200">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            If the model cannot load, the app still works. Use the manual
            check-in or skip this page entirely.
          </div>
        </aside>
      </div>
    </div>
  );
}
