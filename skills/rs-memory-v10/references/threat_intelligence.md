# Threat Intelligence Reference

## Threat Feed Integration

### Feed Aggregator
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import aiohttp
import asyncio
from datetime import datetime, timedelta
from cachetools import TTLCache

class ThreatFeed(ABC):
    """Base class for threat feeds."""
    
    @abstractmethod
    async def lookup(self, ioc: str) -> Dict[str, Any]:
        """Lookup an IOC."""
        pass
    
    @abstractmethod
    async def get_recent(self, hours: int = 24) -> List[Dict]:
        """Get recent threats."""
        pass

class ThreatIntelligenceHub:
    """Central threat intelligence hub."""
    
    def __init__(self):
        self.feeds = {}
        self.cache = TTLCache(maxsize=10000, ttl=3600)
        self.session = None
    
    async def initialize(self):
        """Initialize async session."""
        self.session = aiohttp.ClientSession()
    
    def register_feed(self, name: str, feed: ThreatFeed):
        """Register a threat feed."""
        self.feeds[name] = feed
    
    async def lookup_all(self, ioc: str) -> Dict[str, Any]:
        """Lookup IOC across all feeds."""
        if ioc in self.cache:
            return self.cache[ioc]
        
        results = await asyncio.gather(
            *[feed.lookup(ioc) for feed in self.feeds.values()],
            return_exceptions=True
        )
        
        correlated = self._correlate(results)
        self.cache[ioc] = correlated
        return correlated
    
    def _correlate(self, results: List) -> Dict:
        """Correlate results from multiple feeds."""
        correlated = {
            'found_in': [],
            'confidence': 0,
            'threat_type': None,
            'first_seen': None,
            'last_seen': None,
            'tags': set(),
            'details': {}
        }
        
        for name, result in zip(self.feeds.keys(), results):
            if isinstance(result, Exception):
                continue
            
            if result.get('found'):
                correlated['found_in'].append(name)
                correlated['tags'].update(result.get('tags', []))
                
                if correlated['first_seen'] is None or result.get('first_seen') < correlated['first_seen']:
                    correlated['first_seen'] = result.get('first_seen')
                
                if correlated['last_seen'] is None or result.get('last_seen') > correlated['last_seen']:
                    correlated['last_seen'] = result.get('last_seen')
        
        correlated['confidence'] = len(correlated['found_in']) / len(self.feeds) * 100
        correlated['tags'] = list(correlated['tags'])
        
        return correlated
```

### MITRE ATT&CK Integration
```python
class MITREAttackFeed(ThreatFeed):
    """MITRE ATT&CK framework integration."""
    
    def __init__(self):
        self.base_url = "https://attack.mitre.org/api/v1"
        self.techniques_cache = {}
    
    async def lookup(self, ioc: str) -> Dict:
        """Lookup technique by ID."""
        if ioc.startswith('T'):
            return await self._lookup_technique(ioc)
        return {'found': False}
    
    async def _lookup_technique(self, technique_id: str) -> Dict:
        """Get technique details."""
        # Implementation
        pass
    
    async def get_techniques_for_tactic(self, tactic: str) -> List[Dict]:
        """Get all techniques for a tactic."""
        # Implementation
        pass
    
    def map_detection_to_technique(self, detection: Dict) -> List[str]:
        """Map detection to MITRE techniques."""
        # Implementation
        pass
```

### Shodan Threat Feed
```python
class ShodanThreatFeed(ThreatFeed):
    """Shodan threat intelligence."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.shodan.io"
    
    async def lookup(self, ioc: str) -> Dict:
        """Lookup IP or domain on Shodan."""
        if self._is_ip(ioc):
            return await self._lookup_ip(ioc)
        else:
            return await self._lookup_domain(ioc)
    
    async def _lookup_ip(self, ip: str) -> Dict:
        """Lookup IP address."""
        url = f"{self.base_url}/shodan/host/{ip}?key={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
        
        return {
            'found': 'error' not in data,
            'ip': ip,
            'ports': data.get('ports', []),
            'hostnames': data.get('hostnames', []),
            'vulns': data.get('vulns', []),
            'tags': data.get('tags', []),
            'isp': data.get('isp'),
            'org': data.get('org'),
            'country': data.get('country_name')
        }
    
    async def _lookup_domain(self, domain: str) -> Dict:
        """Lookup domain."""
        # Implementation
        pass
    
    async def get_recent(self, hours: int = 24) -> List[Dict]:
        """Get recent threats from Shodan."""
        # Implementation
        pass
```

### VirusTotal Integration
```python
class VirusTotalFeed(ThreatFeed):
    """VirusTotal threat intelligence."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
    
    async def lookup(self, ioc: str) -> Dict:
        """Lookup IOC on VirusTotal."""
        if self._is_hash(ioc):
            endpoint = "files"
        elif self._is_ip(ioc):
            endpoint = "ip_addresses"
        elif self._is_domain(ioc):
            endpoint = "domains"
        elif self._is_url(ioc):
            endpoint = "urls"
        else:
            return {'found': False}
        
        url = f"{self.base_url}/{endpoint}/{ioc}"
        headers = {"x-apikey": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
        
        if 'error' in data:
            return {'found': False, 'error': data['error']}
        
        attributes = data.get('data', {}).get('attributes', {})
        
        return {
            'found': True,
            'last_analysis_stats': attributes.get('last_analysis_stats', {}),
            'reputation': attributes.get('reputation', 0),
            'tags': attributes.get('tags', []),
            'first_seen': attributes.get('first_submission_date'),
            'last_seen': attributes.get('last_analysis_date'),
            'threat_label': attributes.get('popular_threat_classification', {}).get('suggested_threat_label')
        }
```

## Threat Dashboard

```
┌──────────────────────────────────────────────────────────────┐
│  THREAT INTELLIGENCE DASHBOARD                                │
├──────────────────────────────────────────────────────────────┤
│  Active Threats: 127  │  Critical IOCs: 23  │  Feeds: 6/6   │
├──────────────────────────────────────────────────────────────┤
│  LIVE THREAT FEED                                             │
│  ├── [CRITICAL] New APT campaign detected - T1566.001       │
│  ├── [HIGH] Zero-day in [Software] - CVE-2024-XXXXX         │
│  └── [MEDIUM] New malware variant spotted                   │
├──────────────────────────────────────────────────────────────┤
│  TOP THREAT ACTORS                                            │
│  ├── APT29 - 15 incidents last 24h                          │
│  ├── APT28 - 12 incidents last 24h                          │
│  └── FIN7 - 8 incidents last 24h                            │
├──────────────────────────────────────────────────────────────┤
│  IOC STATISTICS                                               │
│  ├── IPs: 45 tracked                                         │
│  ├── Domains: 78 tracked                                     │
│  ├── Hashes: 234 tracked                                     │
│  └── URLs: 156 tracked                                       │
└──────────────────────────────────────────────────────────────┘
```

## Threat Intel API

```python
class ThreatIntelAPI:
    """Threat intelligence API for RS tools."""
    
    def __init__(self, hub: ThreatIntelligenceHub):
        self.hub = hub
    
    async def check_ip(self, ip: str) -> Dict:
        """Check if IP is malicious."""
        return await self.hub.lookup_all(ip)
    
    async def check_domain(self, domain: str) -> Dict:
        """Check if domain is malicious."""
        return await self.hub.lookup_all(domain)
    
    async def check_hash(self, file_hash: str) -> Dict:
        """Check if file hash is malicious."""
        return await self.hub.lookup_all(file_hash)
    
    async def get_threat_summary(self) -> Dict:
        """Get overall threat summary."""
        # Implementation
        pass
    
    async def search_by_tag(self, tag: str) -> List[Dict]:
        """Search threats by tag."""
        # Implementation
        pass
```
