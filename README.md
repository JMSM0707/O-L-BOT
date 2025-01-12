# O-L-BOT
Open Ledger BOT

Bu yerda roʻyxatdan oʻting: [Open Ledger Dashboard](https://testnet.openledger.xyz/?referral_code=emrdqfdnl4)
Rasshireniyani ko'chirib olish : [Open Ledger Extension](https://chromewebstore.google.com/detail/openledger-node/ekbbplmjjgoobhdlffmgeokalelnmjjc)

## Xususiyat

  - Hisob ma'lumotlarini avtomatik olish
  - Agar siz 1 tani tanlasangiz, avtomatik proksi bilan avtomatik ishga tushirish [foydalaning [Monosans Proxy](https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt)]
  - Agar siz 2 ta tanlasangiz, qo‘lda proksi bilan avtomatik ishga tushirish [Ur shaxsiy proksini manual_proxy.txt-ga joylashtirish]
  - Avtomatik da'vo kundalik ro'yxatdan o'tish
  - Har 30 soniyada yurak urishini avtomatik yuborish
  - Mavzular bilan ko'p hisoblar

## Shart

Python3.9 dan yuqori va PIP o'rnatilganligiga ishonch hosil qiling.

## O'rnatish

1. **Repozitoriy klonlash:**
   ```bash
   git clone https://github.com/JMSM0707/O-L-BOT.git
   ```
   ```bash
   cd O-L-BOT-master
   ```

2. **O'rnatish talablari:**
   ```bash
   python INSTALL.BAT yoki pip install -r requirements.txt #yoki pip3 install -r requirements.txt
   ```

## Konfiguratsiya

- **accounts.txt:** Siz faylni accounts.txt loyiha katalogida topasiz. accounts.txt unda skript formatiga mos keladigan ma'lumotlar mavjudligiga ishonch hosil qiling, aks holda skript ishlamaydi. Mana fayl formatlariga misollar:

  ```bash
  open ledger wallet adresingiz 1
  open ledger wallet adresingiz 2
  ```
- **manual_proxy.txt:** Siz faylni manual_proxy.txt loyiha katalogida topasiz. manual_proxy.txt unda skript formatiga mos keladigan ma'lumotlar mavjudligiga ishonch hosil qiling aks holda skript ishlamaydi. Mana fayl formatlariga misollar:
  ```bash
  http://user:pass@ip:port
  socks4://user:pass@ip:port
  socks5://user:pass@ip:port)
  ```

## Ishga tushurish

```bash
python bot.py #yoki python3 bot.py
```

## Penutup

Ushbu omborga tashrif buyurganingiz uchun tashakkur, kuzatishlar va yulduzchalar shaklida hissa qo'shishni unutmang. Savollaringiz bo'lsa, muammolarga duch kelsangiz yoki yaxshilash bo'yicha takliflaringiz bo'lsa, men bilan bog'laning yoki ushbu GitHub omborida muammoni oching.

**JMSM0707**
