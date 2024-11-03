import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu, Toplevel
import requests
import serial
import time
import serial.tools.list_ports
import os
import threading

# Directories
data_directory = os.path.join(os.getenv('APPDATA'), 'qcathack_data')
os.makedirs(data_directory, exist_ok=True)

required_files = {
    "cathack.png": "https://github.com/Teapot321/qCatHack/raw/main/qCatHack_data/cathack.png",
    "esptool.exe": "https://github.com/Teapot321/qCatHack/raw/refs/heads/main/qCatHack_data/esptool.exe",
    "CH9102.exe": "https://github.com/Teapot321/qCatHack/raw/refs/heads/main/qCatHack_data/CH9102.exe"
}

def check_and_download_files():
    for filename, url in required_files.items():
        file_path = os.path.join(data_directory, filename)
        if not os.path.exists(file_path):
            download_file(url, file_path)

def download_file(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download {file_path}: {e}")

def install_requirements():
    required_packages = [
        "requests",
        "pyserial",
        "tkinterdnd2",
    ]

    for package in required_packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def install_esptool():
    esptool_path = os.path.join(data_directory, 'esptool.exe')
    if not os.path.exists(esptool_path):
        download_file("https://github.com/Teapot321/qCatHack/raw/refs/heads/main/qCatHack_data/esptool.exe", esptool_path)

def install_driver():
    driver_path = os.path.join(data_directory, 'CH9102.exe')
    if not os.path.exists(driver_path):
        download_file("https://github.com/Teapot321/qCatHack/raw/refs/heads/main/qCatHack_data/CH9102.exe", driver_path)

def download_and_install_driver():
    install_driver()
    driver_path = os.path.join(data_directory, "CH9102.exe")

    block_buttons()
    loading_window = Toplevel(root)
    loading_window.title("qCatHack")
    loading_window.geometry("300x100")
    loading_window.configure(bg="#050403")

    loading_label = tk.Label(loading_window, text="Downlading Driver...", bg="#050403", fg="#ffffff", font=("Arial", 14))
    loading_label.pack(pady=20)

    root.update()

    def download_driver():
        try:
            subprocess.run(driver_path, check=True)
            messagebox.showinfo("Success", "Driver installed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install driver: {e}")
        finally:
            loading_window.destroy()
            unblock_buttons()

    threading.Thread(target=download_driver).start()

def get_latest_firmware_url():
    return "https://github.com/Stachugit/CatHack/releases/latest/download/CatHack.bin"

def install_firmware():
    try:
        firmware_url = get_latest_firmware_url()
        firmware_path = os.path.join(data_directory, "latest_firmware.bin")

        response = requests.get(firmware_url)
        with open(firmware_path, 'wb') as f:
            f.write(response.content)
        flash_firmware(firmware_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download firmware: {e}")

def flash_firmware(firmware_path):
    com_port = com_port_var.get()
    esptool_path = os.path.join(data_directory, 'esptool.exe')

    loading_window = Toplevel(root)
    loading_window.title("qCatHack")
    loading_window.geometry("300x100")
    loading_window.configure(bg="#050403")

    loading_label = tk.Label(loading_window, text="Flashing...", bg="#050403", fg="#ffffff", font=("Arial", 14))
    loading_label.pack(pady=20)

    root.update()

    def flash_device():
        try:
            command = [esptool_path, '--port', com_port, '--baud', '1500000', 'write_flash', '0x00000', firmware_path]
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Firmware installed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to flash device: {e}")
        finally:
            loading_window.destroy()
            unblock_buttons()

    threading.Thread(target=flash_device).start()

def start_installation():
    install_button.config(state=tk.DISABLED)
    install_firmware()

def block_buttons():
    install_button.config(state=tk.DISABLED, bg="gray", fg="white")
    com_port_menu.config(state=tk.DISABLED, bg="gray", fg="white")
    driver_button.config(state=tk.DISABLED, bg="gray", fg="white")

def unblock_buttons():
    install_button.config(state=tk.NORMAL, bg="#050403", fg="#ff8e19")
    com_port_menu.config(state=tk.NORMAL, bg="#050403", fg="#ff8e19")
    driver_button.config(state=tk.NORMAL, bg="#050403", fg="#ff8e19")

root = tk.Tk()
root.title("qCatHack")
root.configure(bg="#050403")
root.geometry("600x350")
root.resizable(False, False)

check_and_download_files()

cat_hack_image = tk.PhotoImage(file=os.path.join(data_directory, "cathack.png"))

img = tk.Label(root, image=cat_hack_image, bg="#050403")
img.place(relx=0.5, rely=0.0, anchor='n')

install_button = tk.Button(root, text="Install", command=lambda: threading.Thread(target=start_installation).start(),
                           bg="#050403", fg="#ff8e19", borderwidth=2, relief="solid", highlightbackground="#d9d9d9",
                           highlightcolor="white", font=("Fixedsys", 20))

driver_button = tk.Button(root, text="?", command=download_and_install_driver,
                          bg="#050403", fg="#ff8e19", borderwidth=2, relief="solid", highlightbackground="#d9d9d9",
                          highlightcolor="white", font=("Fixedsys", 11))

com_port_var = StringVar(root)
com_ports = [port for port in serial.tools.list_ports.comports()]
com_port_var.set(com_ports[0].device if com_ports else "No device")

com_port_menu = OptionMenu(root, com_port_var, *[port.device for port in com_ports])
com_port_menu.config(bg="#050403", fg="#ff8e19", highlightbackground="#161615", borderwidth=2)

def on_enter_install(event):
    install_button.config(bg="white", fg="#050403", highlightbackground="#d9d9d9")

def on_leave_install(event):
    install_button.config(bg="#050403", fg="#ff8e19")

def on_enter_driver(event):
    driver_button.config(bg="white", fg="#050403", highlightbackground="#d9d9d9")

def on_leave_driver(event):
    driver_button.config(bg="#050403", fg="#ff8e19")

install_button.bind("<Enter>", on_enter_install)
install_button.bind("<Leave>", on_leave_install)
driver_button.bind("<Enter>", on_enter_driver)
driver_button.bind("<Leave>", on_leave_driver)

install_button.place(relx=0.17, rely=0.11, anchor='center')
com_port_menu.place(relx=0.40, rely=0.11, anchor='center')
driver_button.place(relx=0.31, rely=0.11, anchor='center')

install_esptool()

root.mainloop()