/**
 * Privacy-safe attention estimate for the optional focus check.
 *
 * This is a proxy, not a judgement of a student's mind. It only asks whether
 * the face was visible and roughly turned toward the camera in each sampled
 * frame. No identity, emotion, ability or gaze target is inferred, and no
 * frame is uploaded. The score never affects quiz grading.
 */

const NOSE_X_TOLERANCE = 0.45;
const NOSE_Y_TOLERANCE = 0.95;

export function attentionIndicator(score) {
  if (score >= 75) return "Strong attention signal";
  if (score >= 45) return "Mixed attention signal";
  return "Low attention signal";
}

/**
 * Return true for one frame when the face is present and roughly facing the
 * camera. Eye keypoints are used first because they are scale independent;
 * the bounding box is only a fallback for models without eye keypoints.
 */
export function isAttentiveFrame(detection) {
  if (!detection) return false;

  const keypoints = detection.keypoints || [];
  const rightEye = keypoints[0];
  const leftEye = keypoints[1];
  const nose = keypoints[2];

  if (rightEye && leftEye && nose) {
    const eyeDistance = Math.hypot(rightEye.x - leftEye.x, rightEye.y - leftEye.y);
    if (eyeDistance > 0) {
      const eyeMidX = (rightEye.x + leftEye.x) / 2;
      const eyeMidY = (rightEye.y + leftEye.y) / 2;
      const offsetX = Math.abs(nose.x - eyeMidX) / eyeDistance;
      const offsetY = Math.abs(nose.y - eyeMidY) / eyeDistance;
      return offsetX < NOSE_X_TOLERANCE && offsetY < NOSE_Y_TOLERANCE;
    }
  }

  const box = detection.boundingBox;
  if (!box?.width || !box?.height || !nose) return false;
  const centerX = box.originX + box.width / 2;
  const centerY = box.originY + box.height / 2;
  const offsetX = Math.abs(nose.x - centerX) / (box.width / 2);
  const offsetY = Math.abs(nose.y - centerY) / (box.height / 2);
  return offsetX < 0.35 && offsetY < 0.8;
}

/**
 * Convert counted attentive frames into a 0-100 estimate and plain label.
 * Clamping keeps malformed or partial counts from producing a bad score.
 */
export function measureAttention({ total = 0, attention = 0 } = {}) {
  const samples = Math.max(0, Number(total) || 0);
  const attentive = Math.min(samples, Math.max(0, Number(attention) || 0));
  const score = samples ? Math.round((attentive / samples) * 1000) / 10 : 0;
  return { score, indicator: attentionIndicator(score) };
}
