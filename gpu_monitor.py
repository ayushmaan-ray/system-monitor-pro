import subprocess
import platform


def get_gpu_info():
    system = platform.system()

    try:
        if system == "Windows":
            return get_gpu_windows()

        elif system == "Linux":
            return get_gpu_linux()

        else:
            return {
                "status": "unsupported",
                "gpu_name": "Unknown",
                "gpu_usage": None
            }

    except Exception:
        return {
            "status": "error",
            "gpu_name": "Unknown",
            "gpu_usage": None
        }


def get_gpu_windows():
    try:
        name_output = subprocess.check_output(
            [
                "powershell",
                "-Command",
                "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"
            ],
            stderr=subprocess.DEVNULL
        ).decode()

        gpu_names = [line.strip() for line in name_output.split("\n") if line.strip()]
        gpu_name = gpu_names[0] if gpu_names else "Unknown"

        usage_output = subprocess.check_output(
            [
                "powershell",
                "-Command",
                "(Get-Counter '\\GPU Engine(*)\\Utilization Percentage').CounterSamples | Measure-Object -Property CookedValue -Sum | Select -ExpandProperty Sum"
            ],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        gpu_usage = float(usage_output) if usage_output else None

        return {
            "status": "detected",
            "gpu_name": gpu_name,
            "gpu_usage": round(gpu_usage, 2) if gpu_usage else None
        }

    except:
        return {
            "status": "detected",
            "gpu_name": gpu_name if 'gpu_name' in locals() else "Unknown",
            "gpu_usage": None
        }



def get_gpu_linux():
    try:
        output = subprocess.check_output(
            "lspci | grep -i vga",
            shell=True
        ).decode()

        return {
            "status": "detected",
            "gpu_name": output.strip(),
            "gpu_usage": None
        }

    except:
        return {
            "status": "unsupported",
            "gpu_name": "Unknown",
            "gpu_usage": None
        }
