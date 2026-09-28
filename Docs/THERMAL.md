# Native thermal simulation profile

Installed and tested dependency: ThermalPostProcessAssets 1.0.23 (hashes in dependencies.json). The planned published 1.0.25 update is not installed or validated.

Orion owns WhiteHot/BlackHot materials and initializes the dependency particle materials once. Both polarities share CustomMinMax conversion, matching display bounds, Simple downsampling and 30 Hz imagery. The viewport remains full-rate. Effective width is approximately 640 pixels; height follows the viewport aspect. Above 20x the effective cropped width falls by zoom/20, so 40x has approximately 320 samples across the displayed crop. The engine rounds downsampling dimensions.

The installed engine explicitly supports TemperatureConversionMethod CustomMinMax, Simple downsampling and the documented material controls. The dependency's own sight initializes particle materials and a color effect at camera slot 5; Orion now does the same. Effects are attached to, and removed from, the owned optical camera.

The initial broad-clipping capture used implicit conversion and fixed defaults. An attempted native-weather-only profile rendered nearly black in the reference scene and was rejected. The current profile explicitly uses the dependency's baseline thermal simulation overrides: solar irradiance 50..150 and ambient 15..23. Display min varies -10..10, max 45..65 across the day. Rain/fog reduce visibility separately. These numbers control a game display; they are not sensor measurements or validated Orion specifications. Acquisition uses geometric size and weather estimates, never measured pixel contrast.

Clear-scene captures now retain runway/terrain detail with both polarities. Full clear/rain/fog and dawn/noon/night calibration, digital-detail equivalence and temporal refresh measurements remain acceptance work. Do not describe activation tests as image-quality acceptance.
