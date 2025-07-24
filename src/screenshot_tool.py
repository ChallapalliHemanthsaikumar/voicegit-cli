import os
import sys
import time
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab, ImageDraw, ImageFont, Image
import pyautogui

# Multiple screenshot libraries for better multi-monitor support
try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False
    print("Warning: mss not available. Install with: pip install mss")

try:
    import win32api
    import win32gui
    import win32con
    import win32ui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("Warning: pywin32 not available. Install with: pip install pywin32")

class AdvancedScreenshotTool:
    def __init__(self, save_dir="screenshots"):
        self.save_dir = Path(__file__).parent / save_dir
        self.save_dir.mkdir(exist_ok=True)
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        
        # Get detailed screen information
        self.screens = self._detect_all_monitors()
        self.virtual_screen_bbox = self._get_virtual_screen_bbox()
        
        # Debug: Print detected screens
        self._debug_screen_info()
        
        # Validate screen detection
        self._validate_screen_detection()
    
    def _debug_screen_info(self):
        """Debug function to print screen detection info"""
        print(f"\n🔍 DEBUG: Detected {len(self.screens)} screen(s)")
        for i, screen in enumerate(self.screens):
            print(f"  Screen {i}: {screen}")
    
    def _validate_screen_detection(self):
        """Validate screen detection by checking against actual virtual desktop"""
        try:
            # Get the actual virtual desktop size
            all_screens_img = ImageGrab.grab(all_screens=True)
            actual_width, actual_height = all_screens_img.size
            
            print(f"\n🔍 VALIDATION:")
            print(f"  Actual virtual desktop: {actual_width}x{actual_height}")
            
            # Calculate expected virtual desktop from detected screens
            if self.screens:
                min_x = min(screen['bbox'][0] for screen in self.screens)
                max_x = max(screen['bbox'][0] + screen['bbox'][2] for screen in self.screens)
                expected_width = max_x - min_x
                
                print(f"  Expected from detection: {expected_width}x{actual_height}")
                
                if abs(expected_width - actual_width) > 10:  # Allow small tolerance
                    print(f"  ⚠️  WIDTH MISMATCH! Adjusting screen detection...")
                    self._fix_screen_detection(actual_width, actual_height)
                else:
                    print(f"  ✅ Screen detection appears correct")
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
    
    def _fix_screen_detection(self, actual_width, actual_height):
        """Fix screen detection based on actual virtual desktop size"""
        try:
            print("🔧 Fixing screen detection...")
            
            # Get primary screen size
            primary_size = pyautogui.size()
            
            # Recalculate screens based on actual dimensions
            fixed_screens = []
            
            # Primary screen (always at 0,0)
            primary_screen = {
                'id': 0,
                'name': 'Primary Monitor (Fixed)',
                'bbox': (0, 0, primary_size.width, primary_size.height),
                'size': (primary_size.width, primary_size.height),
                'is_primary': True
            }
            fixed_screens.append(primary_screen)
            
            # Calculate second screen based on actual virtual desktop
            if actual_width > primary_size.width:
                second_screen_width = actual_width - primary_size.width
                second_screen = {
                    'id': 1,
                    'name': 'Extended Monitor (Fixed)',
                    'bbox': (primary_size.width, 0, second_screen_width, primary_size.height),
                    'size': (second_screen_width, primary_size.height),
                    'is_primary': False
                }
                fixed_screens.append(second_screen)
            
            # Update screens
            self.screens = fixed_screens
            self.virtual_screen_bbox = self._get_virtual_screen_bbox()
            
            print("✅ Screen detection fixed!")
            for i, screen in enumerate(self.screens):
                print(f"  Fixed Screen {i}: {screen}")
                
        except Exception as e:
            print(f"❌ Failed to fix screen detection: {e}")
    
    def _detect_all_monitors(self):
        """Enhanced monitor detection with better accuracy"""
        screens = []
        
        # Method 1: Try MSS first (most reliable)
        if HAS_MSS:
            try:
                with mss.mss() as sct:
                    monitors = sct.monitors[1:]  # Skip monitor 0 (all monitors combined)
                    print(f"🔍 MSS: Found {len(monitors)} monitors")
                    
                    for i, monitor in enumerate(monitors):
                        screen = {
                            'id': i,
                            'name': f'MSS Monitor {i+1}',
                            'bbox': (monitor['left'], monitor['top'], monitor['width'], monitor['height']),
                            'rect': (monitor['left'], monitor['top'], 
                                   monitor['left'] + monitor['width'], 
                                   monitor['top'] + monitor['height']),
                            'size': (monitor['width'], monitor['height']),
                            'is_primary': i == 0,
                            'mss_monitor': monitor
                        }
                        screens.append(screen)
                        print(f"  MSS Monitor {i}: left={monitor['left']}, top={monitor['top']}, w={monitor['width']}, h={monitor['height']}")
                    
                    if screens:
                        print(f"✅ Using MSS detection with {len(screens)} monitors")
                        return screens
                        
            except Exception as e:
                print(f"❌ MSS detection failed: {e}")
        
        # Method 2: Enhanced fallback with better coordinate calculation
        return self._enhanced_fallback_detection()
    
    def _enhanced_fallback_detection(self):
        """Enhanced fallback detection with precise coordinate calculation"""
        try:
            print("🔍 Using enhanced fallback detection...")
            
            # Get actual virtual desktop dimensions
            all_screens_img = ImageGrab.grab(all_screens=True)
            total_width, total_height = all_screens_img.size
            print(f"🔍 Virtual desktop: {total_width}x{total_height}")
            
            # Get primary screen size
            primary_size = pyautogui.size()
            print(f"🔍 Primary screen: {primary_size.width}x{primary_size.height}")
            
            screens = []
            
            # Primary monitor (always at 0,0)
            primary_screen = {
                'id': 0,
                'name': 'Primary Monitor',
                'bbox': (0, 0, primary_size.width, primary_size.height),
                'size': (primary_size.width, primary_size.height),
                'is_primary': True
            }
            screens.append(primary_screen)
            
            # Extended monitors calculation
            remaining_width = total_width - primary_size.width
            
            if remaining_width > 0:
                # Extended monitor to the right
                extended_screen = {
                    'id': 1,
                    'name': 'Extended Monitor (Right)',
                    'bbox': (primary_size.width, 0, remaining_width, primary_size.height),
                    'size': (remaining_width, primary_size.height),
                    'is_primary': False
                }
                screens.append(extended_screen)
                print(f"🔍 Extended screen: x={primary_size.width}, y=0, w={remaining_width}, h={primary_size.height}")
            
            print(f"✅ Enhanced fallback found {len(screens)} monitors")
            return screens
            
        except Exception as e:
            print(f"❌ Enhanced fallback failed: {e}")
            # Ultimate fallback
            primary_size = pyautogui.size()
            return [{
                'id': 0,
                'name': 'Default Monitor',
                'bbox': (0, 0, primary_size.width, primary_size.height),
                'size': (primary_size.width, primary_size.height),
                'is_primary': True
            }]
    
    # ==================================================
    # MAIN REQUESTED FUNCTIONS
    # ==================================================
    
    def list_screens(self):
        """List all available screens - returns screen information"""
        print("🖥️  Available Screens:")
        print("=" * 50)
        
        screens_info = []
        for i, screen in enumerate(self.screens):
            primary_text = " (PRIMARY)" if screen.get('is_primary', False) else ""
            screen_info = {
                'id': screen['id'],
                'name': screen['name'],
                'size': screen['size'],
                'position': (screen['bbox'][0], screen['bbox'][1]),
                'is_primary': screen.get('is_primary', False)
            }
            screens_info.append(screen_info)
            
            print(f"Screen {i}: {screen['name']}{primary_text}")
            print(f"  📏 Size: {screen['size'][0]}x{screen['size'][1]}")
            print(f"  📍 Position: ({screen['bbox'][0]}, {screen['bbox'][1]})")
            print()
        
        print(f"Total Screens: {len(self.screens)}")
        print("=" * 50)
        
        return screens_info
    
    def capture_screen(self, screen_number, method='auto', add_timestamp=True):
        """
        Capture screenshot of specific screen by number
        
        Args:
            screen_number (int): Screen number (1 for first screen, 2 for second screen, etc.)
            method (str): Capture method - 'auto', 'pil', 'mss', or 'pyautogui'
            add_timestamp (bool): Add timestamp watermark to image
            
        Returns:
            str: Path to saved screenshot file
        """
        try:
            # Convert to 0-based index
            screen_id = screen_number - 1
            
            if screen_id < 0 or screen_id >= len(self.screens):
                available_screens = list(range(1, len(self.screens) + 1))
                raise ValueError(f"Invalid screen number {screen_number}. Available screens: {available_screens}")
            
            print(f"📸 Capturing Screen {screen_number}...")
            
            # Use the enhanced screenshot method
            if method == 'auto':
                return self._capture_screen_auto(screen_id, add_timestamp)
            elif method == 'pil':
                return self._capture_screen_pil(screen_id, add_timestamp)
            elif method == 'mss':
                return self._capture_screen_mss(screen_id, add_timestamp)
            elif method == 'pyautogui':
                return self._capture_screen_pyautogui(screen_id, add_timestamp)
            else:
                raise ValueError(f"Unknown method: {method}. Available methods: auto, pil, mss, pyautogui")
                
        except Exception as e:
            raise Exception(f"Failed to capture screen {screen_number}: {e}")
    
    def _capture_screen_auto(self, screen_id, add_timestamp=True):
        """Auto method - tries best available method"""
        try:
            # Try MSS first for best multi-monitor support
            if HAS_MSS:
                try:
                    return self._capture_screen_mss(screen_id, add_timestamp)
                except Exception as e:
                    print(f"⚠️  MSS failed: {e}, trying PIL...")
            
            # Try PIL method
            try:
                return self._capture_screen_pil(screen_id, add_timestamp)
            except Exception as e:
                print(f"⚠️  PIL failed: {e}, trying PyAutoGUI...")
            
            # Fallback to PyAutoGUI
            return self._capture_screen_pyautogui(screen_id, add_timestamp)
            
        except Exception as e:
            raise Exception(f"All methods failed for screen {screen_id}: {e}")
    
    def _capture_screen_pil(self, screen_id, add_timestamp=True):
        """PIL method - crop from virtual desktop"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screen = self.screens[screen_id]
            filename = f"screen_{screen_id + 1}_pil_{timestamp}.png"
            filepath = self.save_dir / filename
            
            print(f"🔍 PIL: Capturing screen {screen_id + 1}: {screen['name']}")
            
            # Get full virtual desktop
            all_screens = ImageGrab.grab(all_screens=True)
            
            # Calculate crop coordinates
            left = screen['bbox'][0]
            top = screen['bbox'][1]
            right = left + screen['bbox'][2]
            bottom = top + screen['bbox'][3]
            
            # Validate and adjust coordinates
            right = min(right, all_screens.width)
            bottom = min(bottom, all_screens.height)
            left = max(left, 0)
            top = max(top, 0)
            
            # Crop the specific screen
            screen_image = all_screens.crop((left, top, right, bottom))
            
            if add_timestamp:
                screen_image = self._add_timestamp_watermark(screen_image)
            
            screen_image.save(filepath)
            print(f"✅ PIL: Screen {screen_id + 1} captured successfully")
            print(f"📊 Saved to: {filepath}")
            print(f"📏 Size: {screen_image.size}")
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"PIL capture failed: {e}")
    
    def _capture_screen_mss(self, screen_id, add_timestamp=True):
        """MSS method - direct monitor capture"""
        if not HAS_MSS:
            raise Exception("MSS library not available. Install with: pip install mss")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screen = self.screens[screen_id]
            filename = f"screen_{screen_id + 1}_mss_{timestamp}.png"
            filepath = self.save_dir / filename
            
            print(f"🔍 MSS: Capturing screen {screen_id + 1}: {screen['name']}")
            
            with mss.mss() as sct:
                if 'mss_monitor' in screen:
                    # Use exact MSS monitor data
                    monitor = screen['mss_monitor']
                else:
                    # Create monitor dict from bbox
                    bbox = screen['bbox']
                    monitor = {
                        'left': bbox[0],
                        'top': bbox[1],
                        'width': bbox[2],
                        'height': bbox[3]
                    }
                
                # Capture the screen
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                if add_timestamp:
                    img = self._add_timestamp_watermark(img)
                
                img.save(filepath)
                print(f"✅ MSS: Screen {screen_id + 1} captured successfully")
                print(f"📊 Saved to: {filepath}")
                print(f"📏 Size: {img.size}")
                
                return str(filepath)
                
        except Exception as e:
            raise Exception(f"MSS capture failed: {e}")
    
    def _capture_screen_pyautogui(self, screen_id, add_timestamp=True):
        """PyAutoGUI method - region screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screen = self.screens[screen_id]
            filename = f"screen_{screen_id + 1}_pyautogui_{timestamp}.png"
            filepath = self.save_dir / filename
            
            print(f"🔍 PyAutoGUI: Capturing screen {screen_id + 1}: {screen['name']}")
            
            bbox = screen['bbox']
            screenshot = pyautogui.screenshot(region=bbox)
            
            if add_timestamp:
                screenshot = self._add_timestamp_watermark(screenshot)
            
            screenshot.save(filepath)
            print(f"✅ PyAutoGUI: Screen {screen_id + 1} captured successfully")
            print(f"📊 Saved to: {filepath}")
            print(f"📏 Size: {screenshot.size}")
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"PyAutoGUI capture failed: {e}")
    
    # ==================================================
    # EXISTING METHODS (KEPT FOR COMPATIBILITY)
    # ==================================================
    
    def take_screen_screenshot_pil_improved(self, screen_id=0, add_timestamp=True):
        """Improved PIL screenshot method with better coordinate handling"""
        return self._capture_screen_pil(screen_id, add_timestamp)
    
    def take_screen_screenshot_mss(self, screen_id=0, add_timestamp=True):
        """MSS screenshot method - most reliable for multi-monitor"""
        return self._capture_screen_mss(screen_id, add_timestamp)
    
    def take_screen_screenshot(self, screen_id=0, add_timestamp=True, method='auto'):
        """Enhanced screenshot with improved method selection"""
        return self._capture_screen_auto(screen_id, add_timestamp)
    
    def take_first_screen_screenshot(self, add_timestamp=True, method='auto'):
        return self.capture_screen(1, method, add_timestamp)
    
    def take_second_screen_screenshot(self, add_timestamp=True, method='auto'):
        return self.capture_screen(2, method, add_timestamp)
    
    def capture_all_screens_individually(self, add_timestamp=True, method='auto'):
        file_paths = []
        for i in range(len(self.screens)):
            try:
                filepath = self.capture_screen(i + 1, method, add_timestamp)
                file_paths.append(filepath)
            except Exception as e:
                print(f"❌ Failed to capture screen {i + 1}: {e}")
        return file_paths
    
    def take_all_screens_screenshot(self, add_timestamp=True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_screens_{timestamp}.png"
        filepath = self.save_dir / filename
        
        screenshot = ImageGrab.grab(all_screens=True)
        
        if add_timestamp:
            screenshot = self._add_timestamp_watermark(screenshot)
        
        screenshot.save(filepath)
        print(f"✅ All screens screenshot saved: {filepath}")
        return str(filepath)
    
    def _get_virtual_screen_bbox(self):
        if not self.screens:
            return (0, 0, 1920, 1080)
        
        min_x = min(screen['bbox'][0] for screen in self.screens)
        min_y = min(screen['bbox'][1] for screen in self.screens)
        max_x = max(screen['bbox'][0] + screen['bbox'][2] for screen in self.screens)
        max_y = max(screen['bbox'][1] + screen['bbox'][3] for screen in self.screens)
        
        return (min_x, min_y, max_x - min_x, max_y - min_y)
    
    def _add_timestamp_watermark(self, image):
        try:
            draw = ImageDraw.Draw(image)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            text = f"Captured: {timestamp} | Size: {image.size[0]}x{image.size[1]}"
            
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = image.width - text_width - 10
            y = image.height - text_height - 10
            
            draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], fill=(0, 0, 0, 128))
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            return image
        except Exception:
            return image

# Initialize tool
advanced_screenshot = AdvancedScreenshotTool()

# ==================================================
# CONVENIENCE FUNCTIONS FOR EASY ACCESS
# ==================================================

def list_screens():
    """Quick function to list all available screens"""
    return advanced_screenshot.list_screens()

def capture_screen(screen_number, method='auto'):
    """
    Quick function to capture specific screen
    
    Args:
        screen_number (int): Screen number (1, 2, 3, etc.)
        method (str): Capture method ('auto', 'pil', 'mss', 'pyautogui')
    
    Returns:
        str: Path to saved screenshot
    """
    return advanced_screenshot.capture_screen(screen_number, method)

def capture_screen_1(method='auto'):
    """Capture screen 1 (primary)"""
    return capture_screen(1, method)

def capture_screen_2(method='auto'):
    """Capture screen 2 (secondary)"""
    return capture_screen(2, method)

def capture_screen_3(method='auto'):
    """Capture screen 3 (if available)"""
    return capture_screen(3, method)

def main():
    """Enhanced test function with new API"""
    print("🖥️  Screenshot Tool - Enhanced API")
    print("=" * 50)
    
    # List available screens
    screens_info = list_screens()
    print(screens_info)
    if not screens_info:
        print("❌ No screens detected!")
        return
    
    print("\n📸 Choose option:")
    options = [
        "1. Capture Screen 1 (auto method)",
        "2. Capture Screen 2 (auto method)",
        "3. Capture Screen 1 (PIL method)",
        "4. Capture Screen 2 (PIL method)",
        "5. Capture Screen 1 (MSS method)",
        "6. Capture Screen 2 (MSS method)",
        "7. Capture Screen 1 (PyAutoGUI method)",
        "8. Capture Screen 2 (PyAutoGUI method)",
        "9. Capture all screens individually",
        "10. Test all methods on Screen 2"
    ]
    
    for option in options:
        print(option)
    
    try:
        choice = input("\nEnter choice (1-10): ").strip()
        

                
        if choice == "3":
            filepath = capture_screen_1('pil')
            print(f"📸 Screen 1 (PIL) captured: {filepath}")
            
        elif choice == "4":
            if len(screens_info) >= 2:
                filepath = capture_screen_2('pil')
                print(f"📸 Screen 2 (PIL) captured: {filepath}")
            else:
                print("❌ Screen 2 not available")
                

                
        elif choice == "9":
            filepaths = advanced_screenshot.capture_all_screens_individually()
            print(f"📸 Captured {len(filepaths)} screens:")
            for fp in filepaths:
                print(f"  📁 {fp}")
                
        elif choice == "10":
            if len(screens_info) >= 2:
                print("\n🧪 Testing all methods on Screen 2...")
                methods = ['auto', 'pil', 'mss', 'pyautogui']
                for method in methods:
                    try:
                        if method == 'mss' and not HAS_MSS:
                            print(f"  ❌ {method.upper()}: Not available")
                            continue
                        print(f"  🧪 Testing {method.upper()}...")
                        filepath = capture_screen_2(method)
                        print(f"  ✅ {method.upper()}: Success - {filepath}")
                    except Exception as e:
                        print(f"  ❌ {method.upper()}: Failed - {e}")
            else:
                print("❌ Screen 2 not available")
                
        else:
            print("❌ Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()