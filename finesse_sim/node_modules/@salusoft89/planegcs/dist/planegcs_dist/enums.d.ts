export declare const InternalAlignmentType: {
    readonly EllipsePositiveMajorX: 0;
    readonly EllipsePositiveMajorY: 1;
    readonly EllipseNegativeMajorX: 2;
    readonly EllipseNegativeMajorY: 3;
    readonly EllipsePositiveMinorX: 4;
    readonly EllipsePositiveMinorY: 5;
    readonly EllipseNegativeMinorX: 6;
    readonly EllipseNegativeMinorY: 7;
    readonly EllipseFocus2X: 8;
    readonly EllipseFocus2Y: 9;
    readonly HyperbolaPositiveMajorX: 10;
    readonly HyperbolaPositiveMajorY: 11;
    readonly HyperbolaNegativeMajorX: 12;
    readonly HyperbolaNegativeMajorY: 13;
    readonly HyperbolaPositiveMinorX: 14;
    readonly HyperbolaPositiveMinorY: 15;
    readonly HyperbolaNegativeMinorX: 16;
    readonly HyperbolaNegativeMinorY: 17;
};
export type InternalAlignmentType = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17;
export declare const DebugMode: {
    readonly NoDebug: 0;
    readonly Minimal: 1;
    readonly IterationLevel: 2;
};
export type DebugMode = 0 | 1 | 2;
export declare const Constraint_Alignment: {
    readonly NoInternalAlignment: 0;
    readonly InternalAlignment: 1;
};
export type Constraint_Alignment = 0 | 1;
export declare const SolveStatus: {
    readonly Success: 0;
    readonly Converged: 1;
    readonly Failed: 2;
    readonly SuccessfulSolutionInvalid: 3;
};
export type SolveStatus = 0 | 1 | 2 | 3;
export declare const Algorithm: {
    readonly BFGS: 0;
    readonly LevenbergMarquardt: 1;
    readonly DogLeg: 2;
};
export type Algorithm = 0 | 1 | 2;
