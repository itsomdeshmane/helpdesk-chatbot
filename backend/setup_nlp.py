"""
Setup script for NLP dependencies
Installs spaCy and downloads required language model
"""
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_command(command, description):
    """Run a shell command and log the result"""
    logger.info(f"Running: {description}")
    logger.info(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"✅ {description} - SUCCESS")
        if result.stdout:
            logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - FAILED")
        logger.error(f"Error: {e.stderr}")
        return False


def main():
    """Setup NLP dependencies"""
    logger.info("=" * 60)
    logger.info("Setting up NLP dependencies for Intelligent Entity Matcher")
    logger.info("=" * 60)
    
    # Step 1: Install spaCy and RapidFuzz
    logger.info("\n📦 Step 1: Installing spaCy and RapidFuzz...")
    if not run_command(
        [sys.executable, "-m", "pip", "install", "spacy>=3.7.0", "rapidfuzz>=3.5.2"],
        "Install spaCy and RapidFuzz"
    ):
        logger.error("Failed to install spaCy/RapidFuzz. Exiting.")
        return False
    
    # Step 2: Download spaCy language model
    logger.info("\n📥 Step 2: Downloading spaCy English language model...")
    if not run_command(
        [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
        "Download spaCy model (en_core_web_sm)"
    ):
        logger.warning("⚠️ Failed to download spaCy model. NLP features will use fallback patterns.")
        logger.info("You can manually download later with: python -m spacy download en_core_web_sm")
    
    # Step 3: Verify installation
    logger.info("\n🔍 Step 3: Verifying installation...")
    try:
        import spacy
        from rapidfuzz import fuzz
        
        logger.info("✅ spaCy imported successfully")
        logger.info("✅ RapidFuzz imported successfully")
        
        # Try to load model
        try:
            nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded successfully")
            
            # Test entity recognition
            doc = nlp("Show me tickets in Mumbai with high priority")
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            logger.info(f"✅ Entity recognition working. Test entities: {entities}")
            
        except OSError:
            logger.warning("⚠️ spaCy model not found. Pattern matching will be used as fallback.")
        
        # Test fuzzy matching
        score = fuzz.ratio("city", "City")
        logger.info(f"✅ Fuzzy matching working. Test score: {score}")
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ NLP Setup Complete!")
    logger.info("=" * 60)
    logger.info("\nThe Intelligent Entity Matcher is ready to use.")
    logger.info("It will automatically detect:")
    logger.info("  - Locations (cities, states, countries)")
    logger.info("  - Status values (open, closed, pending)")
    logger.info("  - Priorities (high, medium, low)")
    logger.info("  - Categories and types")
    logger.info("  - Dates and amounts")
    logger.info("  - And much more!")
    logger.info("\nRestart your backend server to use the new features.")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

