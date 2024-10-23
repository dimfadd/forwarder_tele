import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerChannel
from telethon.errors import FloodWaitError

# API ID dan Hash dari my.telegram.org
api_id = '29571344'
api_hash = '83071db94acd379a1242d3be3febd337'
phone = '+6285329869691'
executed_messages_file = "executed_messages.txt"  # File untuk menyimpan ID pesan yang sudah dieksekusi

# Membuat client Telegram
client = TelegramClient('session_name', api_id, api_hash)

# Fungsi untuk membaca semua ID pesan yang sudah dieksekusi dari file
def get_executed_message_ids():
    try:
        with open(executed_messages_file, "r") as file:
            executed_ids = file.read().splitlines()  # Membaca setiap baris (ID pesan)
            return set(executed_ids)  # Mengembalikan sebagai set untuk pencarian cepat
    except FileNotFoundError:
        return set()  # Jika file tidak ditemukan, kembalikan set kosong

# Fungsi untuk menyimpan ID pesan yang sudah dieksekusi ke file
def save_executed_message_id(message_id):
    with open(executed_messages_file, "a") as file:
        file.write(f"{message_id}\n")  # Tambahkan ID pesan baru di baris baru
    print(f"ID pesan {message_id} disimpan ke {executed_messages_file}")

async def main():
    await client.start(phone)

    try:
        # Mengambil entitas channel menggunakan username atau ID publik
        entity = await client.get_entity('https://t.me/+tj36CSPlZMk5Mjg9')  # Ganti dengan URL channel Anda
        channel_id = entity.id
        access_hash = entity.access_hash

        # Menggunakan InputPeerChannel
        channel = InputPeerChannel(channel_id, access_hash)

        # Mengambil entitas grup (ganti dengan URL grup yang Anda buat)
        group_entity = await client.get_entity('https://t.me/+N1eSGCwjoH9jZjU1')  # Ganti dengan URL grup Anda

        # Mendapatkan semua ID pesan yang sudah dieksekusi sebelumnya
        executed_message_ids = get_executed_message_ids()

        # Mengambil pesan dari channel dan mengirimkan ke grup jika belum dieksekusi
        async for message in client.iter_messages(channel):
            if str(message.id) not in executed_message_ids:  # Periksa apakah ID pesan sudah dieksekusi
                if message.text:  # Pastikan pesan bukan None
                    # Format pesan yang akan dikirim ke grup
                    formatted_message = f"Pengirim: {message.sender_id}\nPesan: {message.text}\nTanggal: {message.date}"

                    try:
                        # Mengirim pesan ke grup
                        await client.send_message(group_entity, formatted_message)

                        # Simpan ID pesan yang berhasil dikirim
                        save_executed_message_id(message.id)

                        # Tambahkan ID pesan ke set `executed_message_ids` agar tidak diulang
                        executed_message_ids.add(str(message.id))

                        # Tambahkan jeda untuk menghindari rate limit
                        await asyncio.sleep(5)  # Jeda 5 detik di antara setiap pesan

                    except FloodWaitError as e:
                        # Jika terkena FloodWaitError, tunggu sesuai waktu yang disarankan oleh Telegram
                        print(f"FloodWaitError terjadi. Harus menunggu selama {e.seconds} detik.")
                        await asyncio.sleep(e.seconds)  # Tunggu waktu yang disarankan sebelum melanjutkan
            else:
                print(f"Pesan dengan ID {message.id} sudah dieksekusi, melewati pesan ini.")

        print("Semua pesan baru berhasil dikirim ke grup.")

    except Exception as e:
        print(f"Error: {e}")

# Menjalankan client
with client:
    client.loop.run_until_complete(main())
