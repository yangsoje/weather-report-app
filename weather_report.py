# GitHub Repository: https://github.com/yangsoje/weather-report-app.git
# 작성자 : 양소제
# 파일명: weather_report.py
# 설명: Open-Meteo API를 이용한 날씨 예보 리포트 프로그램

import json
from datetime import datetime
from typing import Optional, Dict, Any
import requests # type: ignore

# Open-Meteo WMO 날씨 코드 매핑
WMO_WEATHER_CODES = {
    0: "맑음",
    1: "주로 맑음", 2: "구름 조금", 3: "흐림",
    45: "안개", 48: "서리 안개",
    51: "이슬비(약함)", 53: "이슬비(보통)", 55: "이슬비(강함)",
    61: "비(약함)", 63: "비(보통)", 65: "비(강함)",
    71: "눈(약함)", 73: "눈(보통)", 75: "눈(강함)",
    80: "소나기(약함)", 81: "소나기(보통)", 82: "소나기(강함)",
    95: "뇌우", 96: "뇌우 및 우박"
}

# 도시별 위도/경도
LOCATION_COORDS = {
    "서울": {"lat": 37.5665, "lon": 126.9780},
    "천안": {"lat": 36.8151, "lon": 127.1139},
    "부산": {"lat": 35.1796, "lon": 129.0756},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "인천": {"lat": 37.4563, "lon": 126.7052},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "대전": {"lat": 36.3510, "lon": 127.3850}
}


def get_weather_data(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Open-Meteo API에서 날씨 데이터를 가져옵니다."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "weather_code", "wind_speed_10m"],
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": "Asia/Seoul",
        "forecast_days": 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ 날씨 정보를 가져오는 중 오류 발생: {e}")
        return None


def parse_and_print_weather(city_name: str, lat: float, lon: float, data: Dict[str, Any]) -> Dict[str, Any]:
    """날씨 리포트를 출력하고 반환용 데이터 구조를 생성합니다."""
    print("=" * 60)
    print(f"☀️ {city_name} 날씨 예보 (오전 6 시 / 오후 3 시 기준)")
    print("=" * 60)

    daily_data = data.get("daily", {})
    hourly_data = data.get("hourly", {})
    
    dates = daily_data.get("time", [])
    report_data = {
        "city": city_name,
        "latitude": lat,
        "longitude": lon,
        "forecast": []
    }

    day_labels = ["오늘", "내일", "모레"]

    for i, date_str in enumerate(dates):
        label = day_labels[i] if i < len(day_labels) else f"{i+1}일후"
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%m.%d.")

        min_temp = round(daily_data["temperature_2m_min"][i])
        max_temp = round(daily_data["temperature_2m_max"][i])

        print(f"\n📅 {label} ({formatted_date})")
        print("-" * 50)

        idx_6 = i * 24 + 6
        idx_15 = i * 24 + 15

        times_to_check = [
            ("🌅 오전 06:00", idx_6),
            ("🌆 오후 15:00", idx_15)
        ]

        day_forecast = {
            "date": date_str,
            "label": label,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "hourly": []
        }

        for time_label, idx in times_to_check:
            w_code = hourly_data["weather_code"][idx]
            weather_desc = WMO_WEATHER_CODES.get(w_code, "정보 없음")
            temp = round(hourly_data["temperature_2m"][idx])
            pop = hourly_data["precipitation_probability"][idx]
            humidity = hourly_data["relative_humidity_2m"][idx]
            wind_speed = round(hourly_data["wind_speed_10m"][idx])

            print(f"  {time_label}")
            print(f"    날씨: {weather_desc}")
            print(f"    기온: {temp} °C")
            print(f"    강수확률: {pop}%")
            print(f"    습도: {humidity}%")
            print(f"    풍속: {wind_speed} m/s\n")

            day_forecast["hourly"].append({
                "time": time_label,
                "weather": weather_desc,
                "temp_c": temp,
                "pop_percent": pop,
                "humidity_percent": humidity,
                "wind_speed_ms": wind_speed
            })

        print(f"  📌 일일 기온: 최저 {min_temp} °C / 최고 {max_temp} °C")
        print("=" * 60)

        report_data["forecast"].append(day_forecast)

    return report_data


def save_to_json(city_name: str, data: Dict[str, Any]):
    """JSON 파일로 결과를 저장합니다."""
    today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"weather_{city_name}_{today_str}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 날씨 정보가 저장되었습니다: {filename}")


def main():
    print("🌤️ 날씨 예보 프로그램 (Open-Meteo API)")
    print("오전 6 시, 오후 3 시 기준으로 3 일간 날씨를 제공합니다.\n")

    user_input = input("날씨를 확인할 지역을 입력하세요 (기본값: 서울): ").strip()
    city_name = user_input if user_input else "서울"

    if city_name in LOCATION_COORDS:
        coords = LOCATION_COORDS[city_name]
        lat, lon = coords["lat"], coords["lon"]
    else:
        print(f"⚠️ '{city_name}' 지역 정보가 없어 기본값(서울)으로 설정합니다.")
        city_name = "서울"
        lat, lon = LOCATION_COORDS["서울"]["lat"], LOCATION_COORDS["서울"]["lon"]

    print(f"\n📍 {city_name} (위도: {lat}, 경도: {lon}) 의 날씨 정보를 가져옵니다...\n")

    weather_raw = get_weather_data(lat, lon)
    if not weather_raw:
        return

    parsed_report = parse_and_print_weather(city_name, lat, lon, weather_raw)

    save_choice = input("\n날씨 정보를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower()
    if save_choice == 'y':
        save_to_json(city_name, parsed_report)


if __name__ == "__main__":
    main()