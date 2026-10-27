/**
 * Safe Navigation & URL Handling Utilities
 * Prevents 404 navigation bugs, malformed relative URLs, and fabricated paths.
 */

/**
 * Ensures an external URL is valid and prefixed with an explicit http(s) scheme
 * so the browser never misinterprets it as a relative path under the local app origin.
 */
export function getSafeUrl(url) {
  if (!url || typeof url !== 'string') return null;
  const trimmed = url.trim();
  if (!trimmed) return null;

  // Reject dangerous schemes
  if (/^(javascript|data|file|vbscript|blob):/i.test(trimmed)) {
    return null;
  }

  // Prepend https:// if no scheme is provided
  if (!/^https?:\/\//i.test(trimmed)) {
    return `https://${trimmed}`;
  }

  return trimmed;
}

/**
 * Checks whether an event has an authentic, reachable registration URL.
 * Returns false if missing, unverified/dead, or flagged as HTTP 404.
 */
export function isRegistrationUrlReachable(event) {
  if (!event || !event.registration_url) return false;

  const url = getSafeUrl(event.registration_url);
  if (!url) return false;

  // If the backend link auditor confirmed 404 or not found, it is NOT reachable
  if (
    event.link_status === 'confirmed_not_found' ||
    event.link_http_status === 404 ||
    event.link_http_status === 410
  ) {
    return false;
  }

  return true;
}

/**
 * Returns the canonical internal React Router route for an event.
 * Uses the human-readable slug when available, falling back to the numeric ID.
 */
export function getInternalEventRoute(event) {
  if (!event) return '/';
  const identifier = event.slug || event.id;
  return identifier ? `/events/${identifier}` : '/';
}

/**
 * Resolves the primary registration action without ever navigating to a 404 page.
 */
export function getRegistrationAction(event) {
  if (!event) {
    return {
      type: 'none',
      label: 'Unavailable',
      isExternal: false,
    };
  }

  const isClosed =
    event.status === 'closed' ||
    (event.registration_deadline && new Date(event.registration_deadline) < new Date());

  if (isClosed) {
    return {
      type: 'closed',
      label: 'Registration Closed',
      isExternal: false,
      internalUrl: getInternalEventRoute(event),
    };
  }

  if (event.status === 'cancelled') {
    return {
      type: 'cancelled',
      label: 'Event Cancelled',
      isExternal: false,
      internalUrl: getInternalEventRoute(event),
    };
  }

  // Check if official direct registration URL is reachable
  if (isRegistrationUrlReachable(event)) {
    return {
      type: 'external',
      label: 'Register',
      fullLabel: 'Register Now',
      url: getSafeUrl(event.registration_url),
      isExternal: true,
      internalUrl: getInternalEventRoute(event),
    };
  }

  // When registration URL is unavailable (missing or confirmed 404),
  // NEVER navigate to a fabricated URL or dead external page.
  // Instead, navigate internally to the event details page.
  return {
    type: 'internal_fallback',
    label: 'View Details',
    fullLabel: 'View Details',
    isExternal: false,
    internalUrl: getInternalEventRoute(event),
    officialWebsiteUrl: getSafeUrl(event.official_website),
    message: 'Registration link unavailable. View event details for more information.',
  };
}
