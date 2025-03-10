
{
  "dns": {
    "hosts": {
      "geosite:category-porn": "127.0.0.1",
      "domain:googleapis.cn": "googleapis.com"
    },
    "servers": [
      "https://8.8.8.8/dns-query"
    ]
  },
  "inbounds": [
    {
      "listen": "127.0.0.1",
      "port": 10808,
      "protocol": "socks",
      "settings": {
        "auth": "noauth",
        "udp": true,
        "userLevel": 8
      },
      "sniffing": {
        "destOverride": [
          "http",
          "tls"
        ],
        "enabled": true
      },
      "tag": "socks"
    },
    {
      "listen": "127.0.0.1",
      "port": 10809,
      "protocol": "http",
      "settings": {
        "userLevel": 8
      },
      "tag": "http"
    }
  ],
  "log": {
    "loglevel": "warning"
  },
  "outbounds": [
    {
      "mux": {
        "concurrency": -1,
        "enabled": false,
        "xudpConcurrency": 8,
        "xudpProxyUDP443": ""
      },
      "protocol": "wireguard",
      "settings": {
        "address": [
          "172.16.0.2/32"
        ],
        "mtu": 1330,
        "peers": [
          {
            "endpoint": "188.114.96.55:1843",
            "keepAlive": 10,
            "preSharedKey": "",
            "publicKey": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="
          }
        ],
        "reserved": [
          62,
          93,
          210
        ],
        "secretKey": "YHH7Sp+NtFzqVaPbnQrqmEXKXk0rM1q9BnXyGIPrWEE=",
        "wnoise": "m4",
        "wnoisecount": "25-50",
        "wnoisedelay": "3-6",
        "wpayloadsize": "50-100"
      },
      "tag": "proxy"
    },
    {
      "protocol": "freedom",
      "settings": {},
      "tag": "direct"
    },
    {
      "protocol": "blackhole",
      "settings": {
        "response": {
          "type": "http"
        }
      },
      "tag": "block"
    }
  ],
  "policy": {
    "levels": {
      "8": {
        "connIdle": 300,
        "downlinkOnly": 1,
        "handshake": 4,
        "uplinkOnly": 1
      }
    },
    "system": {
      "statsOutboundUplink": true,
      "statsOutboundDownlink": true
    }
  },
  "remarks": "wire",
  "routing": {
    "domainStrategy": "IPIfNonMatch",
    "rules": [
      {
        "domain": [
          "domain:ir",
          "geosite:category-ir",
          "geosite:private"
        ],
        "outboundTag": "direct",
        "type": "field"
      },
      {
        "ip": [
          "geoip:ir",
          "geoip:private"
        ],
        "outboundTag": "direct",
        "type": "field"
      },
      {
        "domain": [
          "geosite:category-porn"
        ],
        "outboundTag": "block",
        "type": "field"
      },
      {
        "ip": [
          "10.10.34.34",
          "10.10.34.35",
          "10.10.34.36"
        ],
        "outboundTag": "block",
        "type": "field"
      }
    ]
  },
  "stats": {}
}
