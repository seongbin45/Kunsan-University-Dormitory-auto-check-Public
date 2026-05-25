import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# 1. 환경 변수 로드
USER_ID = os.environ.get('USER_ID')
USER_PW = os.environ.get('USER_PW')

# 완료 기록을 저장할 파일 이름
DONE_FILE = "check_done_today_Primary.txt"

def is_already_done():
    """오늘 이미 성공했는지 확인하는 함수"""
    if os.path.exists(DONE_FILE):
        with open(DONE_FILE, "r") as f:
            last_date = f.read().strip()
            if last_date == datetime.now().strftime("%Y-%m-%d"):
                return True
    return False

def mark_as_done():
    """오늘 성공했음을 기록하는 함수"""
    with open(DONE_FILE, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d"))


async def run():
    # 실행하자마자 오늘 이미 했는지 검사
    if is_already_done():
        print("✅ 오늘 일일체크를 이미 완료했습니다. 프로그램을 종료합니다.")
        return 

    async with async_playwright() as p:
        # 1. 브라우저 실행
        print("🚀 브라우저를 실행합니다...")
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            java_script_enabled=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
            
        print("1. 로그인 페이지 접속 및 로그인...")
        await page.goto("https://kis.kunsan.ac.kr/login.do", wait_until="networkidle")

        # 아이디 및 비밀번호 입력
        print("   - 입력창 대기 중...")
        try:
            id_input = page.locator("input#id, input[name='id'], input[type='text']").first
            await id_input.wait_for(state="visible", timeout=15000)
            await id_input.fill(USER_ID)
            
            pw_input = page.locator("input#pw, input[name='pw'], input[type='password']").first
            await pw_input.fill(USER_PW) 
            
            print("   - 정보 입력 완료")
            
            await asyncio.gather(
                page.wait_for_load_state("networkidle"),
                page.keyboard.press("Enter")
            )
            
        except Exception as e:
            print(f"❌ 입력창을 찾을 수 없습니다: {e}")
            await page.screenshot(path="login_error.png")
            await browser.close()
            return

        # 중복 로그인 팝업 처리
        try:
            await asyncio.sleep(2)
            confirm_btn = page.get_by_role("button", name="확인")
            if await confirm_btn.is_visible(timeout=3000):
                await confirm_btn.click()
                print("   - 중복 로그인 확인 클릭")
        except: 
            pass

        # 2. 통합정보 클릭 및 새 탭 감지
        print("2. '통합정보' 클릭 및 새 창 전환 대기...")
        try:
            target_element = page.locator("text='통합정보'").first
            await target_element.wait_for(state="visible", timeout=15000)
            
            async with context.expect_page(timeout=30000) as new_page_info:
                await target_element.dispatch_event("click")
            
            new_tab = await new_page_info.value
            await new_tab.wait_for_load_state("networkidle")
            print("   - 새 창 전환 성공!")
        except Exception as e:
            print(f"❌ 새 창 전환 실패: {e}")
            await browser.close()
            return

        # 3. 학생서비스 탭 클릭
        print("3. '학생서비스' 탭 클릭 중...")
        await asyncio.sleep(5) 
        await new_tab.get_by_text("학생서비스").first.click()

        # 4. 학생생활관 -> 일일체크신청 클릭
        print("4. '학생생활관' -> '일일체크신청' 찾는 중...")
        await asyncio.sleep(3)
        await new_tab.get_by_text("학생생활관").first.click()
        await asyncio.sleep(1)
        await new_tab.get_by_text("일일체크신청").last.click()
        
        # 5. 저장 및 예 클릭
        print("5. '저장' 버튼 클릭 시도...")
        await asyncio.sleep(5) 

        try:
            save_button = new_tab.locator("button:has-text('저장'), input[value='저장'], .btn_save").first
            await save_button.wait_for(state="visible", timeout=15000)
            await save_button.click(force=True)
            print("   - 저장 버튼 클릭 성공!")

        except Exception as e:
            print(f"❌ 저장 버튼을 못 찾았습니다. 프레임 내 수동 탐색 시도...")
            found = False
            for frame in new_tab.frames:
                try:
                    target = frame.get_by_role("button", name="저장").or_(frame.locator("text='저장'"))
                    if await target.count() > 0:
                        await target.first.click()
                        print("   - 프레임 내부에서 저장 버튼 발견 및 클릭!")
                        found = True
                        break
                except: 
                    continue
            
            if not found:
                print("❌ 모든 방법으로도 저장 버튼을 찾을 수 없습니다.")
                await new_tab.screenshot(path="save_button_missing.png")
                await browser.close()
                return

        # 6. '예' 버튼 팝업 독립적 처리
        print("6. 최종 팝업 처리 시작 (엔터키 및 모든 버튼 탐색)...")
        await asyncio.sleep(2) 

        final_success = False
        
        # 1단계: 엔터키 강제 입력
        await new_tab.keyboard.press("Enter")
        print("   - [시도] 엔터키 입력 완료")
        await asyncio.sleep(1)

        # 2단계: 모든 프레임을 뒤져서 수락 버튼 클릭
        for _ in range(10): 
            for f in new_tab.frames:
                try:
                    btns = f.locator("button, input[type='button'], input[type='submit'], a.btn")
                    count = await btns.count()
                    
                    for i in range(count):
                        target = btns.nth(i)
                        txt = await target.inner_text()
                        val = await target.get_attribute("value") or ""
                        
                        if any(x in (txt + val) for x in ["예", "확인", "OK", "yes"]):
                            await target.click(force=True)
                            print(f"   - [성공] '{txt or val}' 버튼을 찾아 클릭했습니다!")
                            final_success = True
                            break
                except: 
                    continue
            
            if final_success: 
                break
            await asyncio.sleep(0.5)

        # 3단계: 브라우저 기본 대화상자 처리
        if not final_success:
            try:
                new_tab.on("dialog", lambda dialog: dialog.accept())
                print("   - [시도] 브라우저 대화상자 자동 수락 시도")
            except: 
                pass

        print("🎉 ✅ 팝업 처리를 완료했습니다. 결과를 확인합니다.")
        await asyncio.sleep(2)
      
        # 7. 사용자 최종 확인 단계
        print("📸 최종 처리 결과를 스크린샷으로 저장합니다...")
        await asyncio.sleep(2)
        
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CHECK_{now}_Primary.png"
        
        await new_tab.screenshot(path=filename)

        # 오늘 성공했음을 파일에 기록
        mark_as_done()
        
        print("\n" + "="*50)
        print(f"✅ 저장 완료: {filename}")
        print("👀 브라우저 화면에서 '일일체크'가 정상적으로 되었는지 확인하세요.")
        print("="*50)



        
        # 8. 팝업 창 닫기
        print("7. '닫기' 버튼 클릭 시도...")
        await asyncio.sleep(3) 

        # 엔터키 강제 입력
        await new_tab.keyboard.press("Enter")
        print("   - [시도] 엔터키 입력 완료")
        await asyncio.sleep(1)

        
        # 9. '로그아웃' 버튼 클릭 (좌표 기반 물리 클릭)
        print("8. '로그아웃' 버튼 클릭 시도 (좌표 및 물리 클릭)...")
        
        try:
            # [보안] 알림창 자동 승인 (로그아웃 하시겠습니까? 확인)
            new_tab.on("dialog", lambda dialog: dialog.accept())

            # 1. '로그아웃' 버튼의 실제 위치(좌표) 찾기
            # 모든 프레임을 뒤져서 버튼 객체를 가져옵니다.
            target_element = None
            for frame in new_tab.frames:
                try:
                    el = frame.get_by_text("로그아웃").first
                    if await el.count() > 0 and await el.is_visible():
                        target_element = el
                        print(f"   - [{frame.name or '프레임'}]에서 버튼 위치 포착!")
                        break
                except: continue

            if target_element:
                # 버튼의 좌표 구하기 (x, y, width, height)
                box = await target_element.bounding_box()
                if box:
                    # 버튼의 정중앙 좌표 계산
                    center_x = box['x'] + box['width'] / 2
                    center_y = box['y'] + box['height'] / 2
                    
                    print(f"   - 버튼 중심 좌표: ({center_x}, {center_y})")
                    
                    # 마우스를 해당 좌표로 이동 후 클릭 (실제 마우스 동작 시뮬레이션)
                    await new_tab.mouse.move(center_x, center_y)
                    await new_tab.mouse.click(center_x, center_y)
                    print("   - 좌표 기반 물리 클릭 완료!")
            else:
                # 2. 버튼을 못 찾을 경우: 화면 우측 상단 강제 클릭 (최후의 수단)
                # 보통 군산대 포털의 로그아웃은 우측 상단에 있으므로 대략적인 위치 클릭
                print("   - 버튼 위치를 잡지 못해 우측 상단 영역(1150, 40)을 강제 클릭합니다.")
                await new_tab.mouse.click(1150, 40) 

        except Exception as e:
            print(f"⚠️ 좌표 클릭 중 예외 발생: {e}")

        # 클릭 신호가 서버에 도달할 시간 충분히 부여
        print("9. 세션 종료 대기 중...")
        await asyncio.sleep(5)


        # 최종 종료 전 대기
        print("10. 모든 작업 완료. 브라우저를 종료합니다.")
        await asyncio.sleep(2)
        
        
        # 5초 대기 후 깔끔하게 종료
        await asyncio.sleep(5) 
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

