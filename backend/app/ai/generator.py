import torch
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from diffusers import (
    StableDiffusionPipeline,
    ControlNetModel,
    StableDiffusionControlNetPipeline,
    DPMSolverMultistepScheduler,
    EulerDiscreteScheduler
)
from PIL import Image
import numpy as np
from app.config import settings
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AIDesignGenerator:
    """Stable Diffusion based architectural design generator"""

    def __init__(self):
        self.device = settings.DEVICE
        self.dtype = torch.float16 if settings.DTYPE == "float16" else torch.float32
        self.pipe = None
        self.controlnet_pipe = None
        self.is_initialized = False
        
        logger.info(f"AIDesignGenerator initialized with device={self.device}, dtype={self.dtype}")

    async def initialize(self):
        """Load and initialize Stable Diffusion pipeline"""
        if self.is_initialized:
            return
        
        try:
            logger.info("Loading Stable Diffusion pipeline...")
            
            # Load base pipeline
            self.pipe = StableDiffusionPipeline.from_pretrained(
                settings.MODEL_ID,
                torch_dtype=self.dtype,
                revision="fp16" if self.dtype == torch.float16 else "main"
            )
            
            # Enable optimization
            self.pipe.to(self.device)
            
            if settings.ENABLE_ATTENTION_SLICING:
                self.pipe.enable_attention_slicing()
            
            if settings.ENABLE_MODEL_CPU_OFFLOAD:
                self.pipe.enable_model_cpu_offload()
            
            logger.info("Stable Diffusion pipeline loaded successfully")
            
            # Load ControlNet pipeline
            logger.info("Loading ControlNet pipeline...")
            controlnet = ControlNetModel.from_pretrained(
                settings.CONTROLNET_MODEL_ID,
                torch_dtype=self.dtype,
                revision="fp16" if self.dtype == torch.float16 else "main"
            )
            
            self.controlnet_pipe = StableDiffusionControlNetPipeline.from_pretrained(
                settings.MODEL_ID,
                controlnet=controlnet,
                torch_dtype=self.dtype,
                revision="fp16" if self.dtype == torch.float16 else "main"
            )
            
            self.controlnet_pipe.to(self.device)
            
            if settings.ENABLE_ATTENTION_SLICING:
                self.controlnet_pipe.enable_attention_slicing()
            
            logger.info("ControlNet pipeline loaded successfully")
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI pipelines: {e}")
            raise

    def _build_architecture_prompt(
        self,
        base_prompt: str,
        climate_zone: str,
        building_type: str,
        orientation: int
    ) -> str:
        """
        Build enriched prompt with climate and context information.
        
        Args:
            base_prompt: User-provided prompt
            climate_zone: Climate zone type
            building_type: Type of building
            orientation: Building orientation (degrees)
            
        Returns:
            Enhanced prompt
        """
        # Climate-specific keywords
        climate_keywords = {
            "tropical": "open ventilation, breezeways, large overhangs, shade structures",
            "temperate": "balanced windows, seasonal shading, efficient glazing",
            "desert": "thick walls, minimal openings, thermal mass, courtyards",
            "cold": "double glazing, thermal insulation, south-facing windows"
        }
        
        # Building type specifics
        building_keywords = {
            "residential": "living spaces, bedrooms, kitchens, natural light",
            "commercial": "open floor plans, meeting spaces, professional aesthetics",
            "institutional": "multipurpose spaces, accessibility, community design",
            "hospitality": "elegant spaces, guest amenities, functional design"
        }
        
        # Orientation descriptions
        orientation_descriptions = {
            (0, 45): "north-facing facade",
            (45, 135): "east-facing facade, morning light",
            (135, 225): "south-facing facade, optimal sun",
            (225, 315): "west-facing facade, afternoon exposure",
            (315, 360): "north-facing facade"
        }
        
        def get_orientation_desc():
            for (start, end), desc in orientation_descriptions.items():
                if start <= orientation <= end:
                    return desc
            return "south-facing"
        
        climate = climate_zone.lower()
        building = building_type.lower()
        
        climate_desc = climate_keywords.get(climate, climate)
        building_desc = building_keywords.get(building, building)
        orientation_desc = get_orientation_desc()
        
        # Combine into enriched prompt
        enhanced_prompt = f"""Architectural conceptual design for a {building} building in {climate} climate.
        {base_prompt}
        Design features: {climate_desc}.
        Building type: {building_desc}.
        Facade orientation: {orientation_desc}.
        Style: modern architecture, sustainable design, professional architectural visualization.
        Quality: high detail, architectural rendering quality, daylight visualization."""
        
        return enhanced_prompt

    async def generate_design(
        self,
        prompt: str,
        climate_zone: str,
        building_type: str,
        orientation: int,
        seed: Optional[int] = None,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate architectural design from text prompt.
        
        Args:
            prompt: Design description
            climate_zone: Climate zone type
            building_type: Building type
            orientation: Orientation in degrees
            seed: Random seed for reproducibility
            guidance_scale: Guidance scale for diffusion
            num_inference_steps: Number of inference steps
            
        Returns:
            Tuple of (image_path, metadata)
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Build enhanced prompt
            enhanced_prompt = self._build_architecture_prompt(
                prompt, climate_zone, building_type, orientation
            )
            
            # Set seed for reproducibility
            if seed is None:
                seed = np.random.randint(0, 2**32 - 1)
            
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            logger.info(f"Generating design with seed={seed}")
            
            # Generate image
            image = self.pipe(
                prompt=enhanced_prompt,
                negative_prompt="blurry, low quality, distorted, ugly",
                generator=generator,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                height=768,
                width=768
            ).images[0]
            
            # Save image
            image_filename = f"design_{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = Path(settings.GENERATED_IMAGES_DIR) / image_filename
            image.save(image_path)
            
            # Create thumbnail
            thumb = image.copy()
            thumb.thumbnail((256, 256))
            thumb_filename = f"thumb_{image_filename}"
            thumb_path = Path(settings.GENERATED_IMAGES_DIR) / thumb_filename
            thumb.save(thumb_path)
            
            metadata = {
                "original_prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "climate_zone": climate_zone,
                "building_type": building_type,
                "orientation": orientation,
                "seed": seed,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_inference_steps,
                "image_size": (768, 768),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Design generated successfully: {image_path}")
            return str(image_path), str(thumb_path), metadata
        
        except Exception as e:
            logger.error(f"Design generation failed: {e}")
            raise

    async def generate_from_sketch(
        self,
        sketch_image: Image.Image,
        prompt: str,
        controlnet_conditioning_scale: float = 1.0,
        seed: Optional[int] = None,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate architectural design from sketch using ControlNet.
        
        Args:
            sketch_image: PIL Image of sketch
            prompt: Design prompt
            controlnet_conditioning_scale: ControlNet conditioning strength
            seed: Random seed
            guidance_scale: Guidance scale
            num_inference_steps: Number of inference steps
            
        Returns:
            Tuple of (image_path, metadata)
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Resize sketch to 768x768
            sketch_image = sketch_image.resize((768, 768))
            
            # Set seed
            if seed is None:
                seed = np.random.randint(0, 2**32 - 1)
            
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            logger.info(f"Generating from sketch with seed={seed}")
            
            # Generate image
            image = self.controlnet_pipe(
                prompt=prompt,
                image=sketch_image,
                negative_prompt="blurry, low quality, distorted",
                generator=generator,
                guidance_scale=guidance_scale,
                controlnet_conditioning_scale=controlnet_conditioning_scale,
                num_inference_steps=num_inference_steps,
                height=768,
                width=768
            ).images[0]
            
            # Save image
            image_filename = f"sketch_design_{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = Path(settings.GENERATED_IMAGES_DIR) / image_filename
            image.save(image_path)
            
            # Create thumbnail
            thumb = image.copy()
            thumb.thumbnail((256, 256))
            thumb_filename = f"thumb_{image_filename}"
            thumb_path = Path(settings.GENERATED_IMAGES_DIR) / thumb_filename
            thumb.save(thumb_path)
            
            metadata = {
                "prompt": prompt,
                "seed": seed,
                "guidance_scale": guidance_scale,
                "controlnet_conditioning_scale": controlnet_conditioning_scale,
                "num_inference_steps": num_inference_steps,
                "image_size": (768, 768),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Sketch-based design generated: {image_path}")
            return str(image_path), str(thumb_path), metadata
        
        except Exception as e:
            logger.error(f"Sketch-based generation failed: {e}")
            raise

    def _generate_design_reasoning(
        self,
        prompt: str,
        climate_zone: str,
        building_type: str,
        orientation: int,
        environmental_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Generate explainable AI reasoning for design choices.
        
        Args:
            prompt: Original design prompt
            climate_zone: Climate zone
            building_type: Building type
            orientation: Orientation
            environmental_scores: Optional environmental analysis scores
            
        Returns:
            AI reasoning dictionary
        """
        reasoning = {
            "design_reasoning": f"Design generated in response to: '{prompt}' for a {building_type} in {climate_zone} climate with {orientation}° orientation.",
            "top_influencing_factors": [
                f"Climate zone ({climate_zone}): Influences ventilation and solar control strategies",
                f"Orientation ({orientation}°): Determines natural light and thermal gain patterns",
                f"Building type ({building_type}): Drives functional space organization",
                "Sustainable design principles: Incorporated passive design strategies"
            ],
            "environmental_summary": f"Design optimized for {climate_zone} climate conditions with appropriate orientation.",
            "optimization_suggestions": []
        }
        
        if environmental_scores:
            if environmental_scores.get("sustainability_index", 0) < 70:
                reasoning["optimization_suggestions"].append(
                    "Consider increasing window overhangs for better solar control"
                )
            if environmental_scores.get("energy_efficiency_score", 0) < 65:
                reasoning["optimization_suggestions"].append(
                    "Enhance cross-ventilation through strategic opening placement"
                )
        
        if not reasoning["optimization_suggestions"]:
            reasoning["optimization_suggestions"].append(
                "Design demonstrates good sustainability performance"
            )
        
        return reasoning


# Global instance
ai_generator = None


async def get_ai_generator() -> AIDesignGenerator:
    """Get or create AI generator instance"""
    global ai_generator
    if ai_generator is None:
        ai_generator = AIDesignGenerator()
        await ai_generator.initialize()
    return ai_generator
