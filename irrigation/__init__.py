"""
Alur yang perlu diperhatikan:
1. mencoba untuk membuat koneksi, bila tidak ada led merah menyala
2. bila ada koneksi, gunakan nptime.settime()
3. bila tidak ada koneksi, ambil data dari local file
4. bila tidak ada maka pass (kita gunakan data dari device)

Next:
Untuk penjadwalan, kita fokus untuk offline. data diambil dari device semua jadwalnya.

- bila ada koneksi kirimkan notifikasi telah berjalan
- bila tidak ada koneksi simpan kedalam file

- ada loop yang gunanya untuk mengecek file apakah notifikasi sudah dikirim atau belum


Next:
kita pikirkan subscriber nya, ini mudah. Tapi client.subscribe("#") harus diberi try except, sehingga ketika
ada error dia tidak mati

"""