export type UrgencyLevel = 'expired' | 'urgent' | 'soon' | 'normal' | 'none';

export function getUrgencyLevel(expirationDate: string | null): UrgencyLevel {
  if (!expirationDate) return 'none';

  const now = new Date();
  const expiry = new Date(expirationDate);
  const diffMs = expiry.getTime() - now.getTime();
  const diffDays = diffMs / (1000 * 60 * 60 * 24);

  if (diffDays < 0) return 'expired';
  if (diffDays <= 1) return 'urgent';
  if (diffDays <= 3) return 'soon';
  return 'normal';
}

export function getUrgencyColor(level: UrgencyLevel): string {
  switch (level) {
    case 'expired': return '#9CA3AF';
    case 'urgent': return '#EF4444';
    case 'soon': return '#F59E0B';
    case 'normal': return '#10B981';
    case 'none': return '#6B7280';
  }
}

export function formatExpiryText(expirationDate: string | null, displayText: string | null): string {
  if (!expirationDate && displayText) return displayText;
  if (!expirationDate) return 'No expiration';

  const now = new Date();
  const expiry = new Date(expirationDate);
  const diffMs = expiry.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return 'Expired';
  if (diffDays === 0) return 'Expires today';
  if (diffDays === 1) return 'Expires tomorrow';
  if (diffDays <= 7) return `Expires in ${diffDays} days`;

  return `Expires ${expiry.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
}
