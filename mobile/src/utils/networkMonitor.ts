/**
 * Service de monitoring des requêtes réseau
 * Permet de vérifier si l'application consomme des données
 */

interface NetworkRequest {
  method: string;
  endpoint: string;
  timestamp: string;
  status: 'BLOCKED' | 'ALLOWED' | 'FAILED';
  reason?: string;
  size?: number;
}

class NetworkMonitor {
  private requests: NetworkRequest[] = [];
  private maxLogs = 100; // Garder les 100 dernières requêtes

  logRequest(request: NetworkRequest): void {
    this.requests.push(request);
    
    // Garder seulement les N dernières requêtes
    if (this.requests.length > this.maxLogs) {
      this.requests.shift();
    }
    
    // Les requêtes ne sont plus loggées pour réduire le bruit
  }

  getBlockedRequests(): NetworkRequest[] {
    return this.requests.filter(r => r.status === 'BLOCKED');
  }

  getAllowedRequests(): NetworkRequest[] {
    return this.requests.filter(r => r.status === 'ALLOWED');
  }

  getStats(): {
    total: number;
    blocked: number;
    allowed: number;
    failed: number;
    lastRequest?: NetworkRequest;
  } {
    const blocked = this.getBlockedRequests().length;
    const allowed = this.getAllowedRequests().length;
    const failed = this.requests.filter(r => r.status === 'FAILED').length;
    
    return {
      total: this.requests.length,
      blocked,
      allowed,
      failed,
      lastRequest: this.requests[this.requests.length - 1],
    };
  }

  clear(): void {
    this.requests = [];
  }

  getReport(): string {
    const stats = this.getStats();
    const recentBlocked = this.getBlockedRequests().slice(-10);
    
    let report = `\n=== RAPPORT DE MONITORING RÉSEAU ===\n`;
    report += `Total requêtes: ${stats.total}\n`;
    report += `✅ Autorisées: ${stats.allowed}\n`;
    report += `🚫 Bloquées: ${stats.blocked}\n`;
    report += `❌ Échecs: ${stats.failed}\n\n`;
    
    if (recentBlocked.length > 0) {
      report += `Dernières requêtes bloquées:\n`;
      recentBlocked.forEach(req => {
        report += `  - ${req.method} ${req.endpoint} (${req.timestamp})\n`;
      });
    }
    
    report += `\n=====================================\n`;
    
    return report;
  }
}

export const networkMonitor = new NetworkMonitor();









