# Research: 멀티 스레드 폴링 엔진

**Date**: 2025-10-31
**Feature**: 003-polling-engine

## Research Topics

### 1. Python Threading 모범 사례

**Decision**: threading.Thread 클래스 사용, daemon=False로 안전한 종료 보장

**Rationale**:
- Python의 threading 모듈은 OS 레벨 스레드를 제공하며 동시 I/O 작업에 적합
- daemon=False로 설정하여 메인 프로그램 종료 시 폴링 스레드도 안전하게 종료
- threading.Event를 사용한 스레드 종료 신호 처리 (stop_event.is_set() 확인)
- 각 폴링 그룹은 독립적인 Thread 인스턴스로 관리

**Alternatives considered**:
- asyncio: PLC 통신이 blocking I/O이고 Feature 2에서 이미 threading 기반이므로 부적합
- multiprocessing: 프로세스 간 데이터 공유 복잡도 증가, 오버헤드 큼
- concurrent.futures.ThreadPoolExecutor: 폴링 그룹별 독립 제어 어려움

### 2. 스레드 안전 큐 설계

**Decision**: queue.Queue 사용 (기본 FIFO, maxsize=10000)

**Rationale**:
- Python queue.Queue는 스레드 안전하게 구현되어 있음 (내부적으로 Lock 사용)
- put()/get() 메서드가 자동으로 동기화 처리
- maxsize로 메모리 사용량 제한 가능
- get_nowait()/put_nowait()로 non-blocking 옵션 제공

**Alternatives considered**:
- collections.deque + threading.Lock: 직접 동기화 구현 필요, 복잡도 증가
- multiprocessing.Queue: 프로세스 간 통신용, 이 케이스에는 오버헤드
- 커스텀 큐: 재발명하지 않기 (표준 라이브러리로 충분)

### 3. 타이밍 정확도 (폴링 주기 준수)

**Decision**: time.perf_counter() + 보정 sleep 사용

**Rationale**:
- time.perf_counter()는 고정밀 타이머 (나노초 정확도)
- 폴링 소요 시간을 측정하여 다음 sleep 시간 보정
- 공식: sleep_time = interval - (poll_end - poll_start) - drift_correction
- 누적 드리프트 추적하여 장기 실행 시에도 주기 유지

**Alternatives considered**:
- time.sleep(interval) 단순 반복: 폴링 소요 시간만큼 주기가 밀림
- time.time(): 시스템 시간 변경에 영향받음 (NTP 조정 등)
- threading.Timer: 매번 새 스레드 생성, 오버헤드 큼

### 4. 메모리 누수 방지

**Decision**: 명시적 리소스 정리 + 약한 참조 패턴

**Rationale**:
- 스레드 종료 시 큐 참조 해제
- 폴링 데이터는 dict로 전달 후 즉시 큐 저장 (로컬 변수로 생명주기 제한)
- PoolManager는 Feature 2에서 관리 (with context manager 사용)
- 주기적 gc.collect() 호출 불필요 (자동 GC로 충분)

**Alternatives considered**:
- weakref 사용: 폴링 데이터는 단방향 흐름이라 불필요
- 수동 gc.collect(): 성능 저하, 폴링 주기에 영향
- 객체 풀링: 복잡도 증가, 이득 미미

## Technology Stack

- **Core**: Python 3.11+ threading, queue, time
- **Dependencies**: Feature 2 PoolManager (PLC 통신)
- **Testing**: pytest, pytest-timeout, unittest.mock

## Performance Considerations

- 폴링 주기 최소값: 100ms (PLC 부담 고려)
- 큐 최대 크기: 10000개 (약 10분치 데이터, 1초 주기 x 10 그룹)
- 스레드 오버헤드: 스레드당 약 8MB 메모리 (Python 기본)
- CPU 사용률: 스레드당 < 1% (대부분 sleep 상태)

## References

- Python threading documentation: https://docs.python.org/3/library/threading.html
- Python queue documentation: https://docs.python.org/3/library/queue.html
- High-resolution timing: https://docs.python.org/3/library/time.html#time.perf_counter
