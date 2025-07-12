#!/usr/bin/env python3
"""
Test script to verify the consolidated receipt module works correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all consolidated imports work"""
    print("🧪 Testing consolidated receipt module imports...")
    
    try:
        # Test core imports
        print("  📦 Testing core module imports...")
        from src.modules.receipts.core import (
            BaseRootWrapper, TabRootWrapper, IsolatedRootWrapper,
            BaseTabSession, TabSession, IsolatedTabSession, TabSessionFactory
        )
        print("  ✅ Core imports successful")
        
        # Test main application imports
        print("  📦 Testing main application imports...")
        from src.modules.receipts.tabbed_receipt_app import (
            TabbedReceiptAppConsolidated, TabbedReceiptApp, IsolatedTabbedReceiptApp
        )
        print("  ✅ Main application imports successful")
        
        # Test factory functionality
        print("  🏭 Testing TabSessionFactory...")
        user_data = {'test': 'data'}
        
        standard_session = TabSessionFactory.create_session("standard", user_data)
        assert isinstance(standard_session, TabSession), "Standard session should be TabSession"
        print("  ✅ Standard session creation successful")
        
        isolated_session = TabSessionFactory.create_session("isolated", user_data)
        assert isinstance(isolated_session, IsolatedTabSession), "Isolated session should be IsolatedTabSession"
        print("  ✅ Isolated session creation successful")
        
        # Test that isolated session has deep copied data
        user_data['test'] = 'modified'
        assert isolated_session.user_data['test'] == 'data', "Isolated session should have deep copied data"
        print("  ✅ Data isolation verified")
        
        print("🎉 All tests passed! Consolidated module is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backwards_compatibility():
    """Test that the old API still works"""
    print("\n🔄 Testing backwards compatibility...")
    
    try:
        # Test that old class names still work
        from src.modules.receipts.tabbed_receipt_app import TabbedReceiptApp
        print("  ✅ TabbedReceiptApp import successful")
        
        from src.modules.receipts.tabbed_receipt_app import IsolatedTabbedReceiptApp
        print("  ✅ IsolatedTabbedReceiptApp import successful")
        
        print("🎉 Backwards compatibility verified!")
        return True
        
    except Exception as e:
        print(f"❌ Backwards compatibility error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting consolidated receipt module tests...\n")
    
    # Run import tests
    imports_ok = test_imports()
    
    # Run backwards compatibility tests
    compat_ok = test_backwards_compatibility()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"  Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Backwards Compatibility: {'✅ PASS' if compat_ok else '❌ FAIL'}")
    
    if imports_ok and compat_ok:
        print("\n🎉 All tests passed! The consolidation is successful.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())