from vood.core.logger import configure_logging, get_logger

if __name__ == "__main__":
    # Test different configurations

    print("=== Test 1: Default console logging ===")
    configure_logging(level="INFO")
    logger = get_logger()
    logger.debug("This won't show (DEBUG < INFO)")
    logger.info("This shows on console")
    logger.warning("This is a warning")
    logger.error("This is an error")

    print("\n=== Test 2: Silent mode ===")
    configure_logging(silent=True)
    logger.info("This is silent - you won't see this")
    print("(nothing logged above)")

    print("\n=== Test 3: File logging only ===")
    configure_logging(level="DEBUG", log_file="test_vood.log", console=False)
    logger.debug("This goes to file only")
    logger.info("This also goes to file only")
    print("(check test_vood.log)")

    print("\n=== Test 4: Both console and file ===")
    configure_logging(level="INFO", log_file="test_vood2.log", console=True)
    logger.info("This goes to both console and file")
    logger.debug("This goes to file only (DEBUG level)")

    print("\n=== Test 5: Silent with file logging ===")
    configure_logging(silent=True, log_file="test_silent.log")
    logger.error("This error is silent on console but in file")
    print("(check test_silent.log)")
