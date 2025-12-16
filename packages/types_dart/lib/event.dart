class MinimalParameters {
  final double dx;
  final double dy;
  final double zoomDelta;
  final double rotDelta;
  final bool inputTrigger;
  final HoloFrame? holoFrame;

  const MinimalParameters({
    required this.dx,
    required this.dy,
    required this.zoomDelta,
    required this.rotDelta,
    required this.inputTrigger,
    this.holoFrame,
  });

  factory MinimalParameters.fromJson(Map<String, dynamic> json) {
    return MinimalParameters(
      dx: (json['POINTER_DELTA']['dx'] as num).toDouble(),
      dy: (json['POINTER_DELTA']['dy'] as num).toDouble(),
      zoomDelta: (json['ZOOM_DELTA'] as num).toDouble(),
      rotDelta: (json['ROT_DELTA'] as num).toDouble(),
      inputTrigger: json['INPUT_TRIGGER'] as bool,
      holoFrame: json['HOLO_FRAME'] != null ? HoloFrame.fromJson(json['HOLO_FRAME']) : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'POINTER_DELTA': {'dx': dx, 'dy': dy},
        'ZOOM_DELTA': zoomDelta,
        'ROT_DELTA': rotDelta,
        'INPUT_TRIGGER': inputTrigger,
        if (holoFrame != null) 'HOLO_FRAME': holoFrame!.toJson(),
      };
}

class HoloFrame {
  final List<double> quaternion;
  final List<double> translation;
  final String surface;
  final Map<String, dynamic>? metadata;

  const HoloFrame({
    required this.quaternion,
    required this.translation,
    required this.surface,
    this.metadata,
  });

  factory HoloFrame.fromJson(Map<String, dynamic> json) {
    return HoloFrame(
      quaternion: (json['quaternion'] as List).map((e) => (e as num).toDouble()).toList(),
      translation: (json['translation'] as List).map((e) => (e as num).toDouble()).toList(),
      surface: json['surface'] as String,
      metadata: json['metadata'] != null ? Map<String, dynamic>.from(json['metadata'] as Map) : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'quaternion': quaternion,
        'translation': translation,
        'surface': surface,
        if (metadata != null) 'metadata': metadata,
      };
}

class EventEnvelope {
  final String type;
  final double timestamp;
  final MinimalParameters payload;

  const EventEnvelope({required this.type, required this.timestamp, required this.payload});

  factory EventEnvelope.fromJson(Map<String, dynamic> json) {
    return EventEnvelope(
      type: json['type'] as String,
      timestamp: (json['timestamp'] as num).toDouble(),
      payload: MinimalParameters.fromJson(json['payload'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() => {
        'type': type,
        'timestamp': timestamp,
        'payload': payload.toJson(),
      };
}

class AgentFrame {
  final String role;
  final String goal;
  final String sdkSurface;
  final Map<String, double> bounds;
  final Map<String, dynamic> focus;
  final MinimalParameters inputs;
  final List<String> outputs;
  final Map<String, dynamic> safety;
  final Map<String, dynamic>? telemetry;

  const AgentFrame({
    required this.role,
    required this.goal,
    required this.sdkSurface,
    required this.bounds,
    required this.focus,
    required this.inputs,
    required this.outputs,
    required this.safety,
    this.telemetry,
  });

  factory AgentFrame.fromJson(Map<String, dynamic> json) {
    return AgentFrame(
      role: json['role'] as String,
      goal: json['goal'] as String,
      sdkSurface: json['sdk_surface'] as String,
      bounds: (json['bounds'] as Map).map((k, v) => MapEntry(k.toString(), (v as num).toDouble())),
      focus: Map<String, dynamic>.from(json['focus'] as Map),
      inputs: MinimalParameters.fromJson(json['inputs'] as Map<String, dynamic>),
      outputs: (json['outputs'] as List).cast<String>(),
      safety: Map<String, dynamic>.from(json['safety'] as Map),
      telemetry: json['telemetry'] != null ? Map<String, dynamic>.from(json['telemetry'] as Map) : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'role': role,
        'goal': goal,
        'sdk_surface': sdkSurface,
        'bounds': bounds,
        'focus': focus,
        'inputs': inputs.toJson(),
        'outputs': outputs,
        'safety': safety,
        if (telemetry != null) 'telemetry': telemetry,
      };
}
