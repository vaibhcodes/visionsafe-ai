# Dataset Acquisition Plan: VisionSafe AI

## 1. Overview & Principles

VisionSafe AI requires high-fidelity computer vision models and congestion prediction capabilities tailored specifically to **heterogeneous, high-density Indian traffic conditions**. Indian traffic environments feature distinct characteristics:
- High modal diversity: 2-wheelers (scooters, motorcycles), 3-wheelers (auto-rickshaws, e-rickshaws), commercial transport (tempo travellers, mini-trucks, buses), passenger cars, and pedestrians/bicycles.
- Disorganized lane discipline and non-standard vehicle spacing.
- Variable CCTV angles, occlusions, illumination shifts, and weather conditions.

### Strict Budget and Safety Constraints
- **Initial Download Limit**: **15.00 GB total** across all datasets until explicit user sign-off.
- **Safety Reserve**: Minimum **25.00 GB free space** on drive `E:` must remain untouched.
- **Selective Slicing Only**: Full archive downloads (such as the complete BMD-45 ~100GB+ collection) are strictly forbidden. Only bounded subsets with verified manifest hashes and verified license agreements are downloaded.

---

## 2. Target Dataset Investigation & Selection Matrix

| Dataset | Origin / Curator | Total Size | Target Subset Size | License / Terms | Focus & Relevance | Acquisition Strategy |
|---|---|---|---|---|---|---|
| **BMD-45** (Bengaluru Mobility Dataset) | IISc AIM (AI for Integrated Mobility) | ~46k 1080p images (~100+ GB) | **4.5 GB** (~2,500 images + full COCO JSON) | Research / Academic Open Access | 14 fine-grained Indian vehicle classes from 3,679 Safe City CCTV cameras | Download single camera bundle + validation partition via Hugging Face API slice. |
| **UVH-26** (Urban Vision Hackathon Dataset) | IISc AIM (arXiv:2511.02563) | 26,646 1080p frames | **3.5 GB** (~2,000 frames + STAPLE consensus labels) | Open Access (Creative Commons / Research) | 1.8M annotations with STAPLE reliability algorithm across Bangalore corridors | Download validation split focusing on complex arterial intersections. |
| **Indian Traffic Dataset (ITD)** / INDO-HCM | IIT Roorkee / Academic ITS | Multi-GB | **2.5 GB** (~1,500 annotated frames) | Academic Use | Adheres to Indian Highway Capacity Manual vehicle groupings (e.g. PCU weighting) | Targeted download of urban link/midblock samples. |
| **Indian Benchmark Video Clips** | Curated CCTV / Urban Traffic Streams | Variable | **2.5 GB** (3 to 5 high-quality clips, 1-2 min each) | Public Domain / CC / Fair Use | Tracking continuity testing (ByteTrack ID switching, occlusion recovery, counting) | Curate sample videos for Bengaluru, Delhi, and Mumbai junctions. |
| **OpenStreetMap (OSM) Road Network** | Geofabrik / Overpass API | Continental / Sub-national | **1.0 GB** (.osm.pbf & OSMnx graph) | Open Database License (ODbL) | Road topology, link lengths, lane counts, speed limits for routing graphs | Bounded bounding box extract (e.g., Bengaluru Central / ORR corridor). |
| **Synthetic / Augmented Edge Cases** | Generated via pipelines | N/A | **1.0 GB** | Internal | Rain, glare, night-time low-light augmentations | Synthesized on-disk as needed. |
| **TOTAL INITIAL ALLOCATION** | | | **15.0 GB** | | **Strictly compliant with initial budget cap** | |

---

## 3. Class Harmonization Mapping (14 Classes to 7 System Classes)

Raw datasets specify granular categories. VisionSafe AI maps them into standard Passenger Car Unit (PCU) classification used for congestion analytics:

| Unified System Class | BMD-45 / UVH-26 Classes | INDO-HCM Equivalents | PCU Factor |
|---|---|---|---|
| `two_wheeler` | `motorcycle`, `scooter` | Two Wheeler (2W) | 0.50 |
| `auto_rickshaw` | `auto_rickshaw`, `e_rickshaw` | Three Wheeler (3W) | 0.80 |
| `car` | `car`, `jeep`, `suv`, `taxi` | Small Car / Sedan / SUV | 1.00 |
| `lcv` | `tempo_traveller`, `pickup_van`, `mini_truck` | Light Commercial Vehicle | 1.50 |
| `bus` | `bus`, `minibus` | Heavy Passenger Vehicle | 3.00 |
| `truck` | `truck`, `multi_axle_truck`, `trailer` | Heavy Commercial Vehicle | 3.00 |
| `vru` (Vulnerable User)| `bicycle`, `pedestrian` | Non-Motorized Transport | 0.20 |

---

## 4. Phased Acquisition Workflow (Codex Execution)

### Phase 1: Pre-download Inspection & Guardrails
1. Inspect remote file manifests via Hugging Face Hub metadata API (`huggingface_hub.HfApi.list_repo_files`).
2. Run `scripts/storage_guard.py` to confirm Drive `E:` free space >= 25 GB.
3. Calculate prospective download total; assert `total_bytes <= 15 * 1024^3`.

### Phase 2: Slice Extraction
1. **BMD-45 Slice**: Retrieve COCO annotation JSON files (~120 MB) and download only images corresponding to validation split or indexed sequence partition (e.g. `images_001` to `images_003`). Total: <= 4.5 GB.
2. **UVH-26 Slice**: Retrieve STAPLE consensus label file and designated validation set. Total: <= 3.5 GB.
3. **OSM Urban Slice**: Download Bengaluru Outer Ring Road / Central network via `osmnx` or Geofabrik Karnataka `.osm.pbf` extract clipped to bounding box `[12.85, 77.50, 13.10, 77.75]`. Total: <= 0.5 GB.

### Phase 3: Integrity & Format Standardization
1. Verify SHA-256 checksums of retrieved files against downloaded manifests.
2. Convert COCO / STAPLE bounding boxes to standardized YOLOv8 format:
   ```
   data/processed/detection/
   ├── images/{train,val,test}/
   └── labels/{train,val,test}/
   ```
3. Generate dataset summary report `data/processed/dataset_manifest.json` detailing image counts, bounding box distributions, and disk footprint.
