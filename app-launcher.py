#!/usr/bin/env python3

# <xbar.title>App Group Launcher</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>ParkSangYong</xbar.author>
# <xbar.author.github>gkdis6</xbar.author.github>
# <xbar.github>https://github.com/gkdis6/app-group</xbar.github>
# <xbar.image>https://raw.githubusercontent.com/gkdis6/app-group/refs/heads/main/images/app-group-management.png</xbar.image>
# <xbar.desc>Launch predefined groups of applications. Allows easy configuration of app groups.</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>

import os
import json
import sys
import subprocess

# Configuration file for app groups
CONFIG_FILE = os.path.expanduser("~/.xbar_app_groups.json")
# Get the full path of this script
SCRIPT_PATH = os.path.realpath(__file__)

def load_app_groups():
    """Loads app groups from the configuration file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_app_groups(app_groups):
    """Saves app groups to the configuration file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(app_groups, f, indent=2)

def launch_applications(app_paths):
    """Launches a list of applications."""
    for app_path in app_paths:
        try:
            subprocess.Popen(["open", app_path])
        except Exception as e:
            print(f"DEBUG: 앱 실행 실패: {app_path}, 오류: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "launch_group":
        group_name = sys.argv[2]
        app_groups = load_app_groups()
        if group_name in app_groups:
            launch_applications(app_groups[group_name])
        else:
            print(f"오류: {group_name} 그룹을 찾을 수 없습니다.")
        sys.exit(0)
    
    elif len(sys.argv) > 1 and sys.argv[1] == "new_group_prompt":
        script_name = 'tell app "System Events" to display dialog "새 앱 그룹 이름을 입력하세요:" default answer "" with title "새 그룹 만들기" buttons {"확인"} default button 1'
        try:
            result_name = subprocess.run(["/usr/bin/osascript", "-e", script_name], capture_output=True, text=True, check=True)
            group_name = result_name.stdout.strip().split("text returned:")[1].strip()
            if group_name:
                script_apps = 'tell application "Finder" to set selectedItems to choose file of type "app" with prompt "그룹에 추가할 앱을 선택하세요:" with multiple selections allowed'
                try:
                    result_apps = subprocess.run(["/usr/bin/osascript", "-e", script_apps], capture_output=True, text=True, check=True)
                    selected_apps_raw = result_apps.stdout.strip()
                    
                    selected_app_paths = []
                    
                    if selected_apps_raw:
                        try:
                            raw_paths = selected_apps_raw.split(", ")
                            
                            for app_path in raw_paths:
                                if "alias" in app_path:
                                    parts = app_path.split(":")
                                    clean_path = "/" + "/".join(parts[1:])
                                else:
                                    clean_path = app_path
                                
                                clean_path = clean_path.strip('"')
                                
                                if os.path.exists(clean_path):
                                    selected_app_paths.append(clean_path)
                                else:
                                    print(f"DEBUG: 경로가 존재하지 않음: '{clean_path}'")
                        except Exception as e:
                            print(f"DEBUG: 앱 경로 처리 중 오류: {e}")

                    app_groups = load_app_groups()
                    app_groups[group_name] = selected_app_paths
                    save_app_groups(app_groups)
                    print(f"새 그룹 '{group_name}'이(가) 생성되었습니다. | refresh=true")
                except subprocess.CalledProcessError as e:
                    print(f"앱 선택이 취소되었거나 오류 발생: {e.stderr} | refresh=true")
                except Exception as e:
                    print(f"앱 선택 중 예외 발생: {e} | refresh=true")
            else:
                print("그룹 이름이 입력되지 않았습니다. | refresh=true")
        except subprocess.CalledProcessError as e:
            print(f"그룹 생성이 취소되었거나 오류 발생: {e.stderr} | refresh=true")
        except Exception as e:
            print(f"그룹 이름 입력 중 예외 발생: {e} | refresh=true")
        sys.exit(0)


    elif len(sys.argv) > 1 and sys.argv[1] == "delete_group_direct":
        group_name = sys.argv[2]
        app_groups = load_app_groups()
        if group_name in app_groups:
            script_confirm = f'tell app "System Events" to display dialog "정말로 \'{group_name}\' 그룹을 삭제하시겠습니까?" buttons {{"취소", "삭제"}} default button 1 with icon caution'
            try:
                result = subprocess.run(["/usr/bin/osascript", "-e", script_confirm], capture_output=True, text=True, check=True)
                button_pressed = result.stdout.strip()
                if "삭제" in button_pressed:
                    del app_groups[group_name]
                    save_app_groups(app_groups)
                    print(f"'{group_name}' 그룹이 삭제되었습니다. | refresh=true")
                else:
                    print(f"'{group_name}' 그룹 삭제가 취소되었습니다. | refresh=true")
            except subprocess.CalledProcessError:
                print("삭제가 취소되었습니다. | refresh=true")
        else:
            print(f"오류: '{group_name}' 그룹을 찾을 수 없습니다. | refresh=true")
        sys.exit(0)

    print("앱 그룹 실행")
    print("---")

    app_groups = load_app_groups()

    if not app_groups:
        print("설정된 앱 그룹이 없습니다.")
        print("---")
    else:
        for group_name, apps in app_groups.items():
            print(f"{group_name} 그룹 실행 | bash=python3 param1=\"{SCRIPT_PATH}\" param2=launch_group param3={group_name} terminal=false refresh=true")
        print("---")
    
    print("앱 그룹 관리")
    print(f"-- 새 그룹 만들기 | bash=python3 param1=\"{SCRIPT_PATH}\" param2=new_group_prompt terminal=false refresh=true")
    
    if app_groups:
        print("-- 그룹 앱 보기")
        for group_name, apps in app_groups.items():
            print(f"---- {group_name}")
            for app_path in apps:
                try:
                    if not app_path:
                        print("------ (경로 없음)")
                        continue
                        
                    clean_path = app_path.rstrip('/')
                    basename = os.path.basename(clean_path)
                    
                    if basename.endswith('.app'):
                        app_name = basename.replace(".app", "")
                    elif '/' in clean_path:
                        app_name = clean_path.split('/')[-1].replace(".app", "")
                    else:
                        app_name = clean_path.replace(".app", "")
                        
                    print(f"------ {app_name or '(이름 추출 실패)'}")
                except Exception as e:
                    print(f"------ 오류: {e}")
        
        print("-- 그룹 삭제")
        for group_name in app_groups.keys():
            print(f"---- {group_name} | bash=python3 param1=\"{SCRIPT_PATH}\" param2=delete_group_direct param3={group_name} terminal=false refresh=true")
    else:
        print("-- 그룹 앱 보기 (설정된 그룹 없음)")
        print("-- 그룹 삭제 (설정된 그룹 없음)")

if __name__ == "__main__":
    main()
