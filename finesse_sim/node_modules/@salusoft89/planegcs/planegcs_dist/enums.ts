
export const InternalAlignmentType = {
    EllipsePositiveMajorX: 0,
    EllipsePositiveMajorY: 1,
    EllipseNegativeMajorX: 2,
    EllipseNegativeMajorY: 3,
    EllipsePositiveMinorX: 4,
    EllipsePositiveMinorY: 5,
    EllipseNegativeMinorX: 6,
    EllipseNegativeMinorY: 7,
    EllipseFocus2X: 8,
    EllipseFocus2Y: 9,
    HyperbolaPositiveMajorX: 10,
    HyperbolaPositiveMajorY: 11,
    HyperbolaNegativeMajorX: 12,
    HyperbolaNegativeMajorY: 13,
    HyperbolaPositiveMinorX: 14,
    HyperbolaPositiveMinorY: 15,
    HyperbolaNegativeMinorX: 16,
    HyperbolaNegativeMinorY: 17,
    
} as const;
export type InternalAlignmentType = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17;

export const DebugMode = {
    NoDebug: 0,
    Minimal: 1,
    IterationLevel: 2,
    
} as const;
export type DebugMode = 0 | 1 | 2;

export const Constraint_Alignment = {
    NoInternalAlignment: 0,
    InternalAlignment: 1,
    
} as const;
export type Constraint_Alignment = 0 | 1;

export const SolveStatus = {
    Success: 0,
    Converged: 1,
    Failed: 2,
    SuccessfulSolutionInvalid: 3,
    
} as const;
export type SolveStatus = 0 | 1 | 2 | 3;

export const Algorithm = {
    BFGS: 0,
    LevenbergMarquardt: 1,
    DogLeg: 2,
    
} as const;
export type Algorithm = 0 | 1 | 2;
