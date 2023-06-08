HOLD_OBS_ACADEMY = 'obs_academy'
HOLD_RECENT_TRANSFER = 'recent_transfer'
HOLD_RECENT_PROMOTION = 'recent_promotion'
HOLD_PENDING_TRANSFER = 'pending_transfer'
HOLD_RCE_REQUIRED = 'rce_required'
HOLD_VATUSA_DISCIPLINE = 'vatusa_discipline'
HOLD_VATUSA_ADMINISTRATIVE = 'vatusa_administrative'


display_name_map = {
    HOLD_OBS_ACADEMY: "Must complete the VATUSA Academy Basic Exam",
    HOLD_RECENT_TRANSFER: "Recent Transfer",
    HOLD_RECENT_PROMOTION: "Recent Promotion",
    HOLD_PENDING_TRANSFER: "Pending Transfer",
    HOLD_RCE_REQUIRED: "RCE Exam Required",
    HOLD_VATUSA_DISCIPLINE: "Disciplinary Transfer Restriction",
    HOLD_VATUSA_ADMINISTRATIVE: "Administrative Transfer Restriction"
}

manual_release_holds = [
    HOLD_OBS_ACADEMY,
    HOLD_RECENT_TRANSFER,
    HOLD_RECENT_PROMOTION,
    HOLD_RCE_REQUIRED,
    HOLD_VATUSA_DISCIPLINE,
    HOLD_VATUSA_ADMINISTRATIVE
]

manual_apply_holds = [
    HOLD_VATUSA_DISCIPLINE,
    HOLD_VATUSA_ADMINISTRATIVE,
    HOLD_RCE_REQUIRED
]

# promotion_holds restrict the ability to promote the user
promotion_holds = [
    HOLD_OBS_ACADEMY,
    HOLD_RCE_REQUIRED,
    HOLD_VATUSA_DISCIPLINE,
    HOLD_VATUSA_ADMINISTRATIVE
]

# transfer_holds restrict the ability to transfer from one facility to another
transfer_holds = [
    HOLD_OBS_ACADEMY,
    HOLD_RECENT_TRANSFER,
    HOLD_RECENT_PROMOTION,
    HOLD_PENDING_TRANSFER,
    HOLD_RCE_REQUIRED,
    HOLD_VATUSA_DISCIPLINE,
    HOLD_VATUSA_ADMINISTRATIVE,
]

# visit_holds restrict the ability to visit facilities
visit_holds = [
    HOLD_RECENT_TRANSFER,
    HOLD_RECENT_PROMOTION,
    HOLD_RCE_REQUIRED,
    HOLD_VATUSA_DISCIPLINE,
    HOLD_VATUSA_ADMINISTRATIVE,
]

prevent_transfer_roles = [
    'ATM',
    'DATM',
    'TA',
    'FE',
    'EC',
    'WM',
    'INS',
    'MTR',
]