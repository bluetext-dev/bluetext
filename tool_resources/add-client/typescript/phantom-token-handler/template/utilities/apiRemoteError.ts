/*
 * Capture an error calling an API
 */
export class ApiRemoteError extends Error {

    constructor(readonly status: number, readonly code: string, readonly details?: string, readonly data?: any) {
        super(`${status}: ${code}`)
    }
}
